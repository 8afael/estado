from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core import database
from app.core.dicionarios import DICIONARIOS_AVALIACAO
from app.core.auth import require_login
from app.models import models
from app.models.extracao_service import (
    salvar_extracao,
    montar_response,
    buscar_extracao_por_artigo,
)
from app.models.schemas import ExtracaoDadosCreate, ExtracaoDadosUpdate, ExtracaoDadosResponse
from app.models.field_map import DIRECT_COLUMN_FIELDS

router = APIRouter(prefix="/extracao", tags=["extracao"])
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_usuario_logado(request: Request, db: Session) -> models.User:
    username = request.session.get("user")
    usuario = db.query(models.User).filter(models.User.username == username).first()
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuário não autenticado.")
    return usuario


# ---------------------------------------------------------------------------
# PÁGINA HTML
# ---------------------------------------------------------------------------

@router.get("/formulario", response_class=HTMLResponse)
@require_login
async def exibir_formulario_extracao(
    request: Request,
    artigo_id: int,
    db: Session = Depends(get_db),
):
    artigo = db.query(models.ArtigoModel).filter(models.ArtigoModel.id == artigo_id).first()
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado.")

    usuario = _get_usuario_logado(request, db)

    registro = buscar_extracao_por_artigo(db, artigo_id)
    rascunho = montar_response(db, registro) if registro else None

    class UsuarioSessao:
        def __init__(self, username):
            self.username = username

    return templates.TemplateResponse(
        "extracao_form.html",
        {
            "request": request,
            "current_user": UsuarioSessao(usuario.username),
            "artigo_id": artigo.id,          # Q1
            "nome_arquivo": artigo.nome_arquivo,  # Q2
            "artigo_link": artigo.link,
            "usuario_id": usuario.id,
            # dá pra JS pré-preencher via JSON.parse na tag <script> do template,
            # ou o JS pode buscar via GET /extracao/dados/{artigo_id} logo no load
            "rascunho_json": rascunho.model_dump_json() if rascunho else "null",
            "paises_lista": DICIONARIOS_AVALIACAO["paises"],
            "coluna_map": DIRECT_COLUMN_FIELDS, 
        },
    )


# ---------------------------------------------------------------------------
# LEITURA DO RASCUNHO (alternativa via fetch, se preferir não embutir no HTML)
# ---------------------------------------------------------------------------

@router.get("/dados/{artigo_id}", response_model=Optional[ExtracaoDadosResponse])
def obter_dados_extracao(artigo_id: int, db: Session = Depends(get_db)):
    registro = buscar_extracao_por_artigo(db, artigo_id)
    if registro is None:
        return None
    return montar_response(db, registro)


# ---------------------------------------------------------------------------
# AUTOSAVE — recebe só o delta (campos alterados desde o último save)
# ---------------------------------------------------------------------------

@router.post("/autosave", response_model=ExtracaoDadosResponse)
async def autosave_extracao(
    request: Request,
    payload: ExtracaoDadosUpdate,
    db: Session = Depends(get_db),
):
    """
    Salva incrementalmente. Espera receber SÓ os campos que mudaram desde o
    último autosave (Pydantic diferencia isso via model_fields_set — campos
    não enviados no JSON não entram nesse conjunto, mesmo tendo default).

    Primeira chamada para um artigo: cria a linha (precisa vir com
    artigo_id no payload). Chamadas seguintes: envie também o campo
    'extracao_id' seguinte para localizar o registro certo, OU deixe o
    endpoint localizar por artigo_id (mais simples pro front, ver abaixo).
    """
    usuario = _get_usuario_logado(request, db)

    if payload.artigo_id is None:
        raise HTTPException(status_code=400, detail="artigo_id é obrigatório no autosave.")

    artigo = db.query(models.ArtigoModel).filter(models.ArtigoModel.id == payload.artigo_id).first()
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado.")

    registro_existente = buscar_extracao_por_artigo(db, payload.artigo_id)

    if registro_existente is None:
        # primeira vez: precisa criar. usuario_id vem do payload ou da sessão.
        payload.usuario_id = payload.usuario_id or usuario.id
        registro = salvar_extracao(db, payload, extracao_id=None, somente_enviados=True)
    else:
        registro = salvar_extracao(
            db, payload, extracao_id=registro_existente.id, somente_enviados=True
        )

    db.commit()
    db.refresh(registro)
    return montar_response(db, registro)


# ---------------------------------------------------------------------------
# CONCLUSÃO — marca status='concluido' (pode incluir validação mínima)
# ---------------------------------------------------------------------------

@router.post("/concluir/{artigo_id}", response_model=ExtracaoDadosResponse)
def concluir_extracao(artigo_id: int, db: Session = Depends(get_db)):
    registro = buscar_extracao_por_artigo(db, artigo_id)
    if registro is None:
        raise HTTPException(status_code=404, detail="Nenhum rascunho de extração encontrado para este artigo.")

    registro.status = "concluido"
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return montar_response(db, registro)