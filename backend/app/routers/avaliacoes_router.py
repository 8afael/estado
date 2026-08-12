import heapq
import unicodedata
from typing import Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core import database
from app.core.auth import require_login
from app.core.dicionarios import DICIONARIOS_AVALIACAO
from app.models import models

# Roteador com prefixo /avaliacoes (combinado com o root_path="/estado", a rota HTML final será /estado/avaliacoes/resultados/)
router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])

# Configuração do Jinja2 apontando para a pasta de templates
templates = Jinja2Templates(directory="app/templates")

IDIOMAS_VALIDOS = {"ingles", "portugues", "espanhol"}
LITERAL_OUTRO = "outro"

# Pool fixo de avaliadores elegíveis para o 3º avaliador (sua tabela users
# não tem coluna de papel/role, então filtro pelo username). Ajuste aqui se
# a lista mudar. Assumi que a coluna se chama `username` (é o que a rota
# /resultados/ já usa em current_user.username) — me avisa se for outra.
AVALIADORES_3_USERNAMES = [
    "av01", "av02", "av03", "av04", "av06",
    "av11", "av12", "av13", "av14",
]


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


@router.get("/artigos-3/", response_class=HTMLResponse)
@require_login
async def artigos_pendentes_decisao(
    request: Request,
    page: int = 1,
    size: int = 20,
    id: Optional[int] = None,
    codigo: Optional[str] = None,
    idioma: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Lista, em artigos_lista3.html, os artigos atribuídos ao usuário logado
    na tabela avaliacao_3 (3º avaliador) -- cada usuário só vê os artigos
    que FORAM DISTRIBUÍDOS PRA ELE (filtro por usuario_id).

    PREMISSA: assumi que existe uma sessão com o username em
    request.session.get("user") (mesmo padrão da rota /resultados/ acima) e
    que models.User tem uma coluna `username` -- ajuste se o nome real
    for outro.

    PREMISSA sobre "Concluído/Pendente": sigo o mesmo padrão do
    /salvar-avaliacao/ original (etapa=1), que grava o literal "Concluído"
    na coluna `resultado` quando o avaliador envia o formulário.
    """
    username_logado = request.session.get("user")

    usuario = (
        db.query(models.User)
        .filter(models.User.username == username_logado)
        .first()
    )
    if usuario is None:
        raise HTTPException(status_code=403, detail="Usuário não encontrado.")

    query = db.query(models.Avaliacao3Model).filter(
        models.Avaliacao3Model.usuario_id == usuario.id
    )

    if id:
        query = query.filter(models.Avaliacao3Model.artigo_id == id)
    if codigo:
        query = query.filter(models.Avaliacao3Model.codigo.ilike(f"%{codigo}%"))
    if idioma:
        query = query.filter(models.Avaliacao3Model.idioma == idioma)
    if status == "concluido":
        query = query.filter(models.Avaliacao3Model.resultado == "Concluído")
    elif status == "pendente":
        query = query.filter(models.Avaliacao3Model.resultado.is_(None))

    total_registros = query.count()
    total_paginas = max(1, -(-total_registros // size))  # ceil division
    page = max(1, min(page, total_paginas))

    avaliacoes = (
        query.order_by(models.Avaliacao3Model.artigo_id)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    idiomas_lista = sorted(
        {
            row[0]
            for row in db.query(models.ArtigoModel.idioma).distinct().all()
            if row[0]
        }
    )

    class UsuarioSessao:
        def __init__(self, username):
            self.username = username

    current_user = UsuarioSessao(username_logado)

    return templates.TemplateResponse(
        "artigos_lista3.html",
        {
            "request": request,
            "current_user": current_user,
            "avaliacoes": avaliacoes,
            "page": page,
            "size": size,
            "total_registros": total_registros,
            "total_paginas": total_paginas,
            "idiomas_lista": idiomas_lista,
        },
    )


# ---------------------------------------------------------------------------
# FORMULÁRIO DE AVALIAÇÃO — 3º Avaliador (avaliacao_3)
# ---------------------------------------------------------------------------
# Reaproveita o mesmo DICIONARIOS_AVALIACAO usado no formulário de etapa=1
# (app.core.dicionarios), então as opções de idioma/ano/tipo/abordagem/T1-T4
# ficam idênticas às da triagem original — nada inventado aqui.


def _get_avaliacao_3_do_usuario(
    db: Session, artigo_id: int, username_logado: Optional[str]
) -> Tuple[models.Avaliacao3Model, models.User]:
    """
    Busca a linha de avaliacao_3 do artigo, garantindo que ela pertence ao
    usuário logado (evita um avaliador acessar/editar a avaliação de outro).
    """
    usuario = (
        db.query(models.User)
        .filter(models.User.username == username_logado)
        .first()
    )
    if usuario is None:
        raise HTTPException(status_code=403, detail="Usuário não encontrado.")

    avaliacao = (
        db.query(models.Avaliacao3Model)
        .filter(
            models.Avaliacao3Model.artigo_id == artigo_id,
            models.Avaliacao3Model.usuario_id == usuario.id,
        )
        .first()
    )
    if avaliacao is None:
        raise HTTPException(
            status_code=404,
            detail=f"Não há avaliação de 3º avaliador para o artigo {artigo_id} "
            f"atribuída ao usuário {username_logado}.",
        )
    return avaliacao, usuario


@router.get("/avaliacao-3", response_class=HTMLResponse)
@require_login
async def formulario_avaliacao_3(
    request: Request,
    artigo_id: int,
    db: Session = Depends(get_db),
):
    """Renderiza avaliacao3.html com os dados atuais da avaliação (se houver)."""
    username_logado = request.session.get("user")
    avaliacao, _ = _get_avaliacao_3_do_usuario(db, artigo_id, username_logado)

    artigo = db.get(models.ArtigoModel, artigo_id)

    class UsuarioSessao:
        def __init__(self, username):
            self.username = username

    current_user = UsuarioSessao(username_logado)

    return templates.TemplateResponse(
        "avaliacao3.html",
        {
            "request": request,
            "current_user": current_user,
            "artigo_id": artigo_id,
            "artigo_link": artigo.link if artigo else None,
            "avaliacao": avaliacao,
            "dicionarios": DICIONARIOS_AVALIACAO,
        },
    )


@router.post("/salvar-avaliacao-3/")
@require_login
async def salvar_avaliacao_3(
    request: Request,
    artigo_id_real: int = Form(...),
    page: int = Form(1),
    ano_publicacao: int = Form(...),
    idioma: str = Form(...),
    paises_autores: Optional[str] = Form(None),
    pais_estudado: Optional[str] = Form(None),
    tipo_documento: str = Form(...),
    abordagem_metodologica: str = Form(...),
    t1_termos_chave: str = Form(...),
    t2_contexto_publico: str = Form(...),
    t3_tema_institucional: str = Form(...),
    t4_analise_direta: str = Form(...),
    usou_ia: Optional[str] = Form(None),
    ia_prompts: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Salva as respostas do 3º avaliador na linha correspondente de
    avaliacao_3. Segue o mesmo padrão do /salvar-avaliacao/ original
    (etapa=1):
      - `resultado` recebe o literal "Concluído" (marcador de que o
        formulário foi enviado — não é a categoria incluir/excluir/incerto;
        essa é calculada à parte por calcular_resultado_avaliador /
        decisao_final e persistida em ArtigoModel.resultado_final via
        /processar-decisoes-finais).
      - NÃO atualiza a tabela `artigo` (ao contrário do /salvar-avaliacao/
        original) — aqui título/resumo/código são somente-leitura no
        formulário, e a classificação do 3º avaliador é justamente o
        desempate, então não deveria sobrescrever o dado "oficial" do
        artigo com uma resposta que pode divergir da triagem.
    """
    username_logado = request.session.get("user")
    avaliacao, _ = _get_avaliacao_3_do_usuario(db, artigo_id_real, username_logado)

    avaliacao.ano_publicacao = ano_publicacao
    avaliacao.idioma = idioma
    avaliacao.paises_autores = paises_autores
    avaliacao.pais_estudado = pais_estudado
    avaliacao.tipo_documento = tipo_documento
    avaliacao.abordagem_metodologica = abordagem_metodologica
    avaliacao.t1_termos_chave = t1_termos_chave
    avaliacao.t2_contexto_publico = t2_contexto_publico
    avaliacao.t3_tema_institucional = t3_tema_institucional
    avaliacao.t4_analise_direta = t4_analise_direta
    avaliacao.usou_ia = usou_ia
    avaliacao.ia_ferramentas_uso = usou_ia
    avaliacao.ia_prompts = ia_prompts
    avaliacao.observacoes = observacoes
    avaliacao.resultado = "Concluído"

    db.add(avaliacao)

    # Espelha a conclusão em artigo_avaliacoes (etapa=2), mesmo padrão do
    # /salvar-avaliacao/ original pra etapa=1.
    distribuicao = (
        db.query(models.ArtigoAvaliacaoModel)
        .filter(
            models.ArtigoAvaliacaoModel.artigo_id == artigo_id_real,
            models.ArtigoAvaliacaoModel.username == username_logado,
            models.ArtigoAvaliacaoModel.etapa == 2,
        )
        .first()
    )
    if distribuicao:
        distribuicao.status = "concluido"
        db.add(distribuicao)

    db.commit()

    return RedirectResponse(
        url=f"/estado/avaliacoes/artigos-3/?page={page}",
        status_code=303,
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

def _artigos_pendentes_avaliacao_3(db: Session) -> List[Tuple[int, Set[int]]]:
    """
    Retorna [(artigo_id, {usuario_id_a1, usuario_id_a2}), ...] para artigos
    que precisam de 3º avaliador e ainda não têm linha em avaliacao_3.

    Mesma otimização de antes: filtra primeiro por
    `artigo.resultado_final IS NULL` (barato, já persistido por
    /processar-decisoes-finais) antes de carregar/validar as duplas de
    triagem em Python.
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
        for row in db.query(models.Avaliacao3Model.artigo_id)
        .filter(models.Avaliacao3Model.artigo_id.in_(candidatos_ids))
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


class DistribuicaoAvaliacao3Out(BaseModel):
    total_pendentes: int
    atribuidos: List[AtribuicaoOut]
    sem_avaliador_disponivel: List[int]  # artigos onde nenhum avaliador elegível sobrou


@router.post("/distribuir-avaliacao-3", response_model=DistribuicaoAvaliacao3Out)
def distribuir_avaliacao_3(
    avaliadores_ids: Optional[List[int]] = Body(
        default=None,
        embed=True,
        description="Sobrescreve o pool de avaliadores. Se omitido (ou body "
        "vazio {}), usa os usuários definidos em AVALIADORES_3_USERNAMES.",
    ),
    db: Session = Depends(get_db),
):
    """
    Cria, em `avaliacao_3` (tabela separada — `avaliacoes` não é tocada),
    uma linha por artigo pendente de 3º avaliador:
      - exatamente 1 avaliador por artigo (UNIQUE(artigo_id) no banco);
      - nunca o mesmo avaliador que já fez a triagem (etapa=1) daquele artigo;
      - o pool de avaliadores é fixo (AVALIADORES_3_USERNAMES), já que a
        tabela users não tem coluna de papel/role;
      - distribuição balanceada via heap mínimo por carga (mesma lógica do
        endpoint anterior), agora contando a carga em avaliacao_3;
      - só `codigo`/`titulo`/`resumo` vêm preenchidos (copiados do artigo,
        pois são NOT NULL) — os demais campos (t1-t4, ano, idioma, etc.)
        ficam em branco pra o avaliador preencher do zero;
      - `etapa` sempre 2;
      - idempotente: artigos que já têm linha em avaliacao_3 são ignorados.
    """
    if avaliadores_ids is None:
        # TODO: troque models.User pelo nome real da sua classe de
        # usuário, e `username` pela coluna real, se forem diferentes.
        avaliadores_ids = [
            row[0]
            for row in db.query(models.User.id)
            .filter(models.User.username.in_(AVALIADORES_3_USERNAMES))
            .all()
        ]

    if len(avaliadores_ids) < 3:
        raise HTTPException(
            status_code=422,
            detail="É preciso pelo menos 3 avaliadores no pool para distribuir "
            "(cada artigo já tem 2 avaliadores excluídos).",
        )

    # mapa id -> username, pra também gravar/atualizar o registro espelho em
    # artigo_avaliacoes (que referencia o usuário por username, não por id)
    username_por_id = dict(
        db.query(models.User.id, models.User.username)
        .filter(models.User.id.in_(avaliadores_ids))
        .all()
    )

    pendentes = _artigos_pendentes_avaliacao_3(db)

    # carga atual em avaliacao_3 por avaliador, pra balancear entre execuções sucessivas
    contagem_atual = dict(
        db.query(models.Avaliacao3Model.usuario_id, func.count(models.Avaliacao3Model.id))
        .filter(models.Avaliacao3Model.usuario_id.in_(avaliadores_ids))
        .group_by(models.Avaliacao3Model.usuario_id)
        .all()
    )

    heap = [(contagem_atual.get(aid, 0), aid) for aid in avaliadores_ids]
    heapq.heapify(heap)

    atribuidos: List[AtribuicaoOut] = []
    sem_avaliador: List[int] = []

    for artigo_id, excluidos in pendentes:
        buffer: List[Tuple[int, int]] = []
        escolhido: Optional[Tuple[int, int]] = None

        while heap:
            carga, aid = heapq.heappop(heap)
            if aid not in excluidos:
                escolhido = (carga, aid)
                break
            buffer.append((carga, aid))

        for item in buffer:
            heapq.heappush(heap, item)

        if escolhido is None:
            sem_avaliador.append(artigo_id)
            continue

        carga, aid = escolhido
        artigo = db.get(models.ArtigoModel, artigo_id)

        nova_avaliacao_3 = models.Avaliacao3Model(
            usuario_id=aid,
            artigo_id=artigo_id,
            etapa=2,
            codigo=artigo.codigo,
            titulo=artigo.titulo,
            resumo=artigo.resumo,
            # demais campos ficam None/NULL de propósito -- avaliador
            # preenche do zero, sem herdar respostas das triagens anteriores
        )
        db.add(nova_avaliacao_3)

        # Espelha a atribuição em artigo_avaliacoes (mesma tabela usada pra
        # etapa=1), com etapa=2 -- é isso que permite depois filtrar
        # `WHERE etapa = 2` pra listar só as avaliações do 3º avaliador.
        username = username_por_id.get(aid)
        if username is not None:
            registro_existente = (
                db.query(models.ArtigoAvaliacaoModel)
                .filter(
                    models.ArtigoAvaliacaoModel.artigo_id == artigo_id,
                    models.ArtigoAvaliacaoModel.username == username,
                )
                .first()
            )
            if registro_existente:
                # defensivo: não deveria existir (o avaliador nunca é A1/A2
                # do mesmo artigo), mas se existir, só garante etapa/status corretos
                registro_existente.etapa = 2
                registro_existente.status = "pendente"
                db.add(registro_existente)
            else:
                db.add(
                    models.ArtigoAvaliacaoModel(
                        artigo_id=artigo_id,
                        username=username,
                        status="pendente",
                        etapa=2,
                    )
                )

        atribuidos.append(AtribuicaoOut(artigo_id=artigo_id, usuario_id=aid))
        heapq.heappush(heap, (carga + 1, aid))

    db.commit()

    return DistribuicaoAvaliacao3Out(
        total_pendentes=len(pendentes),
        atribuidos=atribuidos,
        sem_avaliador_disponivel=sem_avaliador,
    )