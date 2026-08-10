import unicodedata
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core import database
from app.core.auth import require_login
from app.models import models

# Roteador com prefixo /avaliacoes (combinado com o root_path="/estado", a rota HTML final será /estado/avaliacoes/resultados/)
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
# SCHEMAS E ENDPOINTS DA API (REST JSON)
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