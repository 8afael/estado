from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core import database
from app.core.auth import require_login
from app.models import models

router = APIRouter(prefix="/extracao", tags=["extracao"])
templates = Jinja2Templates(directory="app/templates")

# Pool fixo de avaliadores/extratores autorizados nesta etapa. Igual ao
# padrão de AVALIADORES_3_USERNAMES no avaliacao3_router -- sua tabela
# users não tem coluna de papel/role, então o controle é por username.
# Ajuste esta lista conforme necessário.
EXTRATORES_USERNAMES = {
    "av01", "av02", "av03", "admin"
}

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _get_usuario_autorizado(request: Request, db: Session) -> models.User:
    """
    Garante que o usuário está logado E faz parte do pool fixo de
    extratores. Levanta 401 (não logado) ou 403 (logado, mas sem permissão)
    -- centralize esta função e reuse em TODOS os endpoints da extração,
    não só na listagem, senão a restrição vira só cosmética.
    """
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Usuário não autenticado.")

    usuario = db.query(models.User).filter(models.User.username == username).first()
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuário não autenticado.")

    if usuario.username not in EXTRATORES_USERNAMES:
        raise HTTPException(
            status_code=403,
            detail="Você não está autorizado a acessar a etapa de extração de dados.",
        )
    return usuario

@router.get("/artigos-pendentes/", response_class=HTMLResponse)
@require_login
async def listar_artigos_para_extracao(
    request: Request,
    page: int = 1,
    size: int = 20,
    id: Optional[str] = None,
    codigo: Optional[str] = None,
    idioma: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Lista os artigos com decisão final de inclusão (ArtigoModel.resultado_final
    == 'incluir'), restrito ao pool fixo de EXTRATORES_USERNAMES. Cobre tanto
    os artigos incluídos direto por A1=A2 quanto os que passaram pelo 3º
    avaliador -- qualquer caminho que resulte em 'incluir' aparece aqui.
    """
    usuario = _get_usuario_autorizado(request, db)

    query = db.query(models.ArtigoModel).filter(
        models.ArtigoModel.resultado_final == "incluir"
    )

    if id and id.strip():
        try:
            query = query.filter(models.ArtigoModel.id == int(id))
        except ValueError:
            pass
    if codigo:
        query = query.filter(models.ArtigoModel.codigo.ilike(f"%{codigo}%"))
    if idioma:
        query = query.filter(models.ArtigoModel.idioma == idioma)

    artigo_ids_visiveis = [row.id for row in query.all()]
    extracoes_por_artigo = {
        e.artigo_id: e.status
        for e in db.query(models.ExtracaoDadosModel)
        .filter(models.ExtracaoDadosModel.artigo_id.in_(artigo_ids_visiveis))
        .all()
    } if artigo_ids_visiveis else {}

    if status == "nao_iniciado":
        ids_pendentes = [aid for aid in artigo_ids_visiveis if aid not in extracoes_por_artigo]
        query = query.filter(models.ArtigoModel.id.in_(ids_pendentes or [-1]))
    elif status == "em_andamento":
        ids = [aid for aid, st in extracoes_por_artigo.items() if st == "em_andamento"]
        query = query.filter(models.ArtigoModel.id.in_(ids or [-1]))
    elif status == "concluido":
        ids = [aid for aid, st in extracoes_por_artigo.items() if st == "concluido"]
        query = query.filter(models.ArtigoModel.id.in_(ids or [-1]))

    total_registros = query.count()
    total_paginas = max(1, -(-total_registros // size))
    page = max(1, min(page, total_paginas))

    artigos = (
        query.order_by(models.ArtigoModel.id)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    idiomas_lista = sorted({
        row[0] for row in db.query(models.ArtigoModel.idioma).distinct().all() if row[0]
    })

    class UsuarioSessao:
        def __init__(self, username):
            self.username = username

    return templates.TemplateResponse(
        "avaliacao_final_lista.html",
        {
            "request": request,
            "current_user": UsuarioSessao(usuario.username),
            "artigos": artigos,  # 🆕 renomeado de "avaliacoes"
            "extracoes_por_artigo": extracoes_por_artigo,
            "page": page,
            "size": size,
            "total_registros": total_registros,
            "total_paginas": total_paginas,
            "idiomas_lista": idiomas_lista,
        },
    )