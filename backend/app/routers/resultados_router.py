import heapq
import unicodedata
from typing import Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core import database
from app.core.auth import require_login
from app.models import models

# Roteador com prefixo /avaliacoes (combinado com o root_path="/plataforma/estado", a rota HTML final será /estado/avaliacoes/resultados/)
router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])

# Configuração do Jinja2 apontando para a pasta de templates
templates = Jinja2Templates(directory="app/templates")

IDIOMAS_VALIDOS = {"ingles", "portugues", "espanhol"}
LITERAL_OUTRO = "outro"


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _normalizar(texto: Optional[str]) -> str:
    """minúsculas + sem acento, pra comparar respostas sem depender de digitação exata."""
    if not texto:
        return ""
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto


def calcular_resultado_avaliador(av: models.AvaliacaoModel) -> str:
    ano_e_outro = av.ano_publicacao == 0
    idioma_e_outro = _normalizar(av.idioma) == LITERAL_OUTRO

    respostas = [
        _normalizar(av.t1_termos_chave),
        _normalizar(av.t2_contexto_publico),
        _normalizar(av.t3_tema_institucional),
        _normalizar(av.t4_analise_direta),
    ]
    tem_nao = any(r == "nao" for r in respostas)

    if ano_e_outro or idioma_e_outro or tem_nao:
        return "excluir"

    tem_nao_sei = any(r == "nao sei" for r in respostas)
    if tem_nao_sei:
        return "incerto"

    ano_valido = av.ano_publicacao is not None and 2009 <= av.ano_publicacao <= 2026
    idioma_valido = _normalizar(av.idioma) in IDIOMAS_VALIDOS
    todos_sim = all(r == "sim" for r in respostas)

    if ano_valido and idioma_valido and todos_sim:
        return "incluir"

    return "incerto"


def decisao_final(a1: Optional[str], a2: Optional[str], a3: Optional[str] = None) -> str:
    a1 = _normalizar(a1)
    a2 = _normalizar(a2)
    a3 = _normalizar(a3) if a3 else None

    if a1 == "incluir" and a2 == "incluir":
        return "inclusao_final"
    if a1 == "excluir" and a2 == "excluir":
        return "exclusao_final"

    if a3 is None:
        return "encaminhar_terceiro"

    if a3 == "incluir" and (a1 == "incluir" or a2 == "incluir"):
        return "inclusao_final"
    return "exclusao_final"


# ---------------------------------------------------------------------------
# ROTA QUE SERVE A PÁGINA HTML (Template Jinja2)
# ---------------------------------------------------------------------------

@router.get("/resultados/", response_class=HTMLResponse)
@require_login
async def renderizar_pagina_resultados(request: Request):
    """
    Renderiza o arquivo resultados.html localizado em app/templates.
    URL final no navegador: http://localhost:9000/estado/avaliacoes/resultados/
    """
    username_logado = request.session.get("user")

    class UsuarioSessao:
        def __init__(self, username):
            self.username = username

    current_user = UsuarioSessao(username_logado)

    return templates.TemplateResponse(
        "resultados.html",
        {
            "request": request,
            "current_user": current_user
        }
    )


# ---------------------------------------------------------------------------
# SCHEMAS E ENDPOINTS DA API (REST JSON) — Cálculo de resultado de triagem
# ---------------------------------------------------------------------------

class ResultadoAvaliacaoOut(BaseModel):
    id: int
    artigo_id: int
    usuario_id: int
    etapa: int
    resultado_triagem: str


@router.get("/processar", response_model=List[ResultadoAvaliacaoOut])
def processar_resultados(db: Session = Depends(get_db)):
    avaliacoes = db.query(models.AvaliacaoModel).all()
    return [
        ResultadoAvaliacaoOut(
            id=av.id,
            artigo_id=av.artigo_id,
            usuario_id=av.usuario_id,
            etapa=av.etapa,
            resultado_triagem=calcular_resultado_avaliador(av),
        )
        for av in avaliacoes
    ]


class DecisaoFinalOut(BaseModel):
    artigo_id: int
    a1: Optional[str]
    a2: Optional[str]
    a3: Optional[str]
    decisao_final: str


_MAPA_RESULTADO_FINAL = {
    "inclusao_final": "incluir",
    "exclusao_final": "excluir",
}


@router.get("/artigos/{artigo_id}/decisao-final", response_model=DecisaoFinalOut)
def obter_decisao_final(artigo_id: int, db: Session = Depends(get_db)):
    artigo = db.query(models.ArtigoModel).filter(models.ArtigoModel.id == artigo_id).first()
    if artigo is None:
        raise HTTPException(status_code=404, detail=f"Artigo {artigo_id} não encontrado.")

    triagem = (
        db.query(models.AvaliacaoModel)
        .filter(models.AvaliacaoModel.artigo_id == artigo_id, models.AvaliacaoModel.etapa == 1)
        .order_by(models.AvaliacaoModel.usuario_id)
        .all()
    )
    if len(triagem) != 2:
        raise HTTPException(
            status_code=422,
            detail=f"Esperava 2 avaliações de triagem (etapa=1) para o artigo {artigo_id}, encontrei {len(triagem)}.",
        )

    a1_row, a2_row = triagem
    a1 = calcular_resultado_avaliador(a1_row)
    a2 = calcular_resultado_avaliador(a2_row)

    terceiro = (
        db.query(models.AvaliacaoModel)
        .filter(models.AvaliacaoModel.artigo_id == artigo_id, models.AvaliacaoModel.etapa == 2)
        .first()
    )
    a3 = calcular_resultado_avaliador(terceiro) if terceiro else None

    resultado = decisao_final(a1, a2, a3)

    valor_persistir = _MAPA_RESULTADO_FINAL.get(resultado)
    if valor_persistir is not None:
        artigo.resultado_final = valor_persistir
        db.add(artigo)
        db.commit()

    return DecisaoFinalOut(artigo_id=artigo_id, a1=a1, a2=a2, a3=a3, decisao_final=resultado)


class ProcessamentoFinalOut(BaseModel):
    total_processados: int
    incluidos: int
    excluidos: int
    aguardando_terceiro: int


@router.post("/processar-decisoes-finais", response_model=ProcessamentoFinalOut)
def processar_decisoes_finais(db: Session = Depends(get_db)):
    """
    Roda a decisão final (matriz A1/A2/A3) para TODOS os artigos que tenham
    as 2 avaliações de etapa=1 completas, e persiste `resultado_final` em
    ArtigoModel:
      - 'incluir' / 'excluir' quando a decisão já está fechada;
      - NULL quando o artigo precisa de 3º avaliador (discordância ou
        'incerto' em A1/A2, e o A3 — se já existir em etapa=2 — não fechou
        a decisão).

    É esse `resultado_final IS NULL` que o endpoint de redistribuição usa
    depois como filtro rápido pra achar quem precisa de 3º avaliador, então
    rode este endpoint antes de redistribuir (ou sempre que novas
    avaliações de etapa=1/2 forem lançadas).
    """
    triagens = (
        db.query(models.AvaliacaoModel)
        .filter(models.AvaliacaoModel.etapa == 1)
        .all()
    )
    por_artigo: Dict[int, List[models.AvaliacaoModel]] = {}
    for av in triagens:
        por_artigo.setdefault(av.artigo_id, []).append(av)

    terceiros = (
        db.query(models.AvaliacaoModel)
        .filter(models.AvaliacaoModel.etapa == 2)
        .all()
    )
    terceiro_por_artigo = {av.artigo_id: av for av in terceiros}

    artigo_ids = list(por_artigo.keys())
    artigos = (
        db.query(models.ArtigoModel)
        .filter(models.ArtigoModel.id.in_(artigo_ids))
        .all()
        if artigo_ids
        else []
    )
    artigos_por_id = {a.id: a for a in artigos}

    incluidos = excluidos = aguardando = total = 0

    for artigo_id, avals in por_artigo.items():
        if len(avals) != 2:
            continue  # triagem incompleta, ignora por enquanto

        artigo = artigos_por_id.get(artigo_id)
        if artigo is None:
            continue

        a1_row, a2_row = sorted(avals, key=lambda a: a.usuario_id)
        a1 = calcular_resultado_avaliador(a1_row)
        a2 = calcular_resultado_avaliador(a2_row)

        terceiro = terceiro_por_artigo.get(artigo_id)
        a3 = calcular_resultado_avaliador(terceiro) if terceiro else None

        resultado = decisao_final(a1, a2, a3)
        valor_persistir = _MAPA_RESULTADO_FINAL.get(resultado)  # None se 'encaminhar_terceiro'

        artigo.resultado_final = valor_persistir
        db.add(artigo)

        total += 1
        if valor_persistir == "incluir":
            incluidos += 1
        elif valor_persistir == "excluir":
            excluidos += 1
        else:
            aguardando += 1

    db.commit()

    return ProcessamentoFinalOut(
        total_processados=total,
        incluidos=incluidos,
        excluidos=excluidos,
        aguardando_terceiro=aguardando,
    )


# ---------------------------------------------------------------------------
# REDISTRIBUIÇÃO PARA O 3º AVALIADOR (etapa=2)
# ---------------------------------------------------------------------------
#
# PREMISSA (confirme comigo): não recebi um model de Usuário/Avaliador com
# papel (role) definido, então o "pool" de avaliadores elegíveis é inferido
# como o conjunto de usuario_id distintos que já fizeram alguma avaliação de
# etapa=1 (triagem). Se você tiver uma lista fixa de avaliadores (ex: tabela
# users com role='avaliador'), me avisa que eu troco a origem do pool — ou,
# enquanto isso, dá pra passar `avaliadores_ids` no corpo da requisição pra
# sobrescrever o pool manualmente.

def _artigos_pendentes_terceiro(db: Session) -> List[Tuple[int, Set[int]]]:
    """
    Retorna [(artigo_id, {usuario_id_a1, usuario_id_a2}), ...] para artigos
    que precisam de 3º avaliador e ainda não têm etapa=2 atribuída.

    Otimização: filtra primeiro por `resultado_final IS NULL` direto no
    banco (barato — é o campo já persistido por /processar-decisoes-finais)
    em vez de recarregar e recalcular TODAS as duplas de triagem em Python.
    Só os candidatos que sobram desse filtro são então validados (tem
    exatamente 2 avaliações de etapa=1? ainda não tem etapa=2?).

    IMPORTANTE: rode POST /avaliacoes/processar-decisoes-finais antes deste
    endpoint (ou sempre que novas avaliações forem lançadas), senão
    `resultado_final` pode estar desatualizado.
    """
    candidatos_ids = [
        row[0]
        for row in db.query(models.ArtigoModel.id)
        .filter(models.ArtigoModel.resultado_final.is_(None))
        .all()
    ]
    if not candidatos_ids:
        return []

    ja_tem_terceiro = {
        row[0]
        for row in db.query(models.AvaliacaoModel.artigo_id)
        .filter(
            models.AvaliacaoModel.etapa == 2,
            models.AvaliacaoModel.artigo_id.in_(candidatos_ids),
        )
        .distinct()
        .all()
    }

    triagens = (
        db.query(models.AvaliacaoModel)
        .filter(
            models.AvaliacaoModel.etapa == 1,
            models.AvaliacaoModel.artigo_id.in_(candidatos_ids),
        )
        .order_by(models.AvaliacaoModel.artigo_id, models.AvaliacaoModel.usuario_id)
        .all()
    )

    por_artigo: Dict[int, List[models.AvaliacaoModel]] = {}
    for av in triagens:
        por_artigo.setdefault(av.artigo_id, []).append(av)

    pendentes: List[Tuple[int, Set[int]]] = []
    for artigo_id, avals in por_artigo.items():
        if artigo_id in ja_tem_terceiro or len(avals) != 2:
            continue  # triagem incompleta ou já tem 3º avaliador -> não é "pendente"
        a1_row, a2_row = avals
        a1 = calcular_resultado_avaliador(a1_row)
        a2 = calcular_resultado_avaliador(a2_row)
        if decisao_final(a1, a2) == "encaminhar_terceiro":
            pendentes.append((artigo_id, {a1_row.usuario_id, a2_row.usuario_id}))

    return pendentes


class AtribuicaoOut(BaseModel):
    artigo_id: int
    usuario_id: int


class RedistribuicaoOut(BaseModel):
    total_pendentes: int
    atribuidos: List[AtribuicaoOut]
    sem_avaliador_disponivel: List[int]  # artigos onde nenhum avaliador elegível sobrou


@router.post("/redistribuir-terceiro-avaliador", response_model=RedistribuicaoOut)
def redistribuir_terceiro_avaliador(
    avaliadores_ids: Optional[List[int]] = Body(
        default=None,
        embed=True,
        description="Sobrescreve o pool de avaliadores. Se omitido (ou body "
        "vazio {}), usa os usuario_id distintos que já fizeram triagem (etapa=1).",
    ),
    db: Session = Depends(get_db),
):
    """
    Distribui, entre os avaliadores disponíveis, os artigos cuja triagem
    (etapa=1) precisa de um 3º avaliador — criando uma linha nova em
    `avaliacoes` com etapa=2 para cada um.

    Regras aplicadas:
      - um avaliador nunca recebe um artigo que ele mesmo avaliou na etapa=1;
      - cada artigo recebe exatamente 1 avaliação de etapa=2 (nunca mais de uma);
      - a distribuição é balanceada: a cada atribuição, escolhe-se o avaliador
        elegível com MENOR carga atual de etapa=2 (empates resolvidos pelo
        menor usuario_id) — isso mantém o total por avaliador o mais parelho
        possível mesmo quando alguns avaliadores ficam inelegíveis em vários
        artigos.
      - é idempotente: rodar de novo não duplica atribuições já feitas
        (artigos que já têm etapa=2 são ignorados) e considera a carga já
        existente no banco, então chamadas sucessivas continuam balanceando
        corretamente.

    Sobre a complexidade: em vez de recalcular "quem tem menos carga" a cada
    artigo (O(n·k)), uso um heap mínimo por carga (O(n·log k)) — quando um
    avaliador é pulado por ser A1/A2 do artigo, ele volta pro heap sem perder
    a posição relativa.
    """
    if avaliadores_ids is None:
        avaliadores_ids = [
            row[0]
            for row in db.query(models.AvaliacaoModel.usuario_id)
            .filter(models.AvaliacaoModel.etapa == 1)
            .distinct()
            .all()
        ]

    if len(avaliadores_ids) < 3:
        raise HTTPException(
            status_code=422,
            detail="É preciso pelo menos 3 avaliadores no pool para redistribuir "
            "(cada artigo já tem 2 avaliadores excluídos).",
        )

    pendentes = _artigos_pendentes_terceiro(db)

    # carga atual de etapa=2 por avaliador, pra balancear mesmo entre execuções sucessivas
    contagem_atual = dict(
        db.query(models.AvaliacaoModel.usuario_id, func.count(models.AvaliacaoModel.id))
        .filter(
            models.AvaliacaoModel.etapa == 2,
            models.AvaliacaoModel.usuario_id.in_(avaliadores_ids),
        )
        .group_by(models.AvaliacaoModel.usuario_id)
        .all()
    )

    heap = [(contagem_atual.get(aid, 0), aid) for aid in avaliadores_ids]
    heapq.heapify(heap)

    atribuidos: List[AtribuicaoOut] = []
    sem_avaliador: List[int] = []

    for artigo_id, excluidos in pendentes:
        buffer: List[Tuple[int, int]] = []
        escolhido: Optional[Tuple[int, int]] = None

        # desempilha até achar alguém que não seja A1/A2 deste artigo
        while heap:
            carga, aid = heapq.heappop(heap)
            if aid not in excluidos:
                escolhido = (carga, aid)
                break
            buffer.append((carga, aid))

        # devolve pro heap quem foi descartado só por causa da exclusão
        for item in buffer:
            heapq.heappush(heap, item)

        if escolhido is None:
            sem_avaliador.append(artigo_id)
            continue

        carga, aid = escolhido
        artigo = db.get(models.ArtigoModel, artigo_id)

        nova_avaliacao = models.AvaliacaoModel(
            usuario_id=aid,
            artigo_id=artigo_id,
            etapa=2,
            codigo=artigo.codigo,
            titulo=artigo.titulo,
            resumo=artigo.resumo,
        )
        db.add(nova_avaliacao)
        atribuidos.append(AtribuicaoOut(artigo_id=artigo_id, usuario_id=aid))
        heapq.heappush(heap, (carga + 1, aid))

    db.commit()

    return RedistribuicaoOut(
        total_pendentes=len(pendentes),
        atribuidos=atribuidos,
        sem_avaliador_disponivel=sem_avaliador,
    )