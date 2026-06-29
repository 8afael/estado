from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, contains_eager
from math import ceil
from typing import Optional
from app.models import models
from app.core import database
from app.core.auth import require_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@require_login
@router.api_route("/artigos/", methods=["GET", "POST"], response_class=HTMLResponse)
async def listar_artigos_avaliador(
    request: Request,
    page: int = 1,
    size: int = 20,
    id: Optional[str] = None,     
    codigo: Optional[str] = None,
    idioma: Optional[str] = None,
    status: Optional[str] = None,    
    db: Session = Depends(get_db)
):
    # 1. PEGA O USUÁRIO DIRETO DA SESSÃO
    username_logado = request.session.get("user")
    
    class UsuarioSessao:
        def __init__(self, username):
            self.username = username
    current_user = UsuarioSessao(username_logado)

    # 2. Se for um POST vindo dos filtros da tabela
    if request.method == "POST":
        form_data = await request.form()
        
        v_id = form_data.get("id", "")
        v_codigo = form_data.get("codigo", "")
        v_idioma = form_data.get("idioma", "")
        v_status = form_data.get("status", "")
        
        url_redirecionamento = f"/estado/artigos/?page=1&size={size}&id={v_id}&codigo={v_codigo}&idioma={v_idioma}&status={v_status}"
        return RedirectResponse(url=url_redirecionamento, status_code=303)

    # --- FLUXO DO GET ---

    # 3. Busca os idiomas apenas dos artigos designados a este usuário para o <select>
    idiomas_lista = [
        r[0] for r in db.query(models.ArtigoModel.idioma)\
        .join(models.ArtigoAvaliacaoModel, models.ArtigoModel.id == models.ArtigoAvaliacaoModel.artigo_id)\
        .filter(models.ArtigoAvaliacaoModel.username == username_logado)\
        .distinct().all() if r[0]
    ]

    # 4. CONSTRUÇÃO DA QUERY CORRIGIDA
    user_db = db.query(models.User).filter(models.User.username == username_logado).first()
    
    query = db.query(models.ArtigoModel)\
    .join(
        models.ArtigoAvaliacaoModel, 
        (models.ArtigoModel.id == models.ArtigoAvaliacaoModel.artigo_id) & 
        (models.ArtigoAvaliacaoModel.username == username_logado)
    )\
    .outerjoin(
        models.AvaliacaoModel, 
        (models.ArtigoModel.id == models.AvaliacaoModel.artigo_id) & 
        (models.AvaliacaoModel.usuario_id == user_db.id)
    )\
    .options(contains_eager(models.ArtigoModel.avaliacoes))\
    .populate_existing()
    
    # --- FILTROS ---
    if id and id.strip() != "":
        try: query = query.filter(models.ArtigoModel.id == int(id))
        except ValueError: pass 
            
    if codigo and codigo.strip() != "":
        query = query.filter(models.ArtigoModel.codigo.ilike(f"%{codigo}%"))
        
    if idioma and idioma.strip() != "":
        query = query.filter(models.ArtigoModel.idioma == idioma)
        
    if status and status.strip() != "":
        st_lower = status.lower()
        if st_lower in ["concluido", "concluído"]:
            # 🟢 Usa a tabela intermediária que agora foi devidamente vinculada (Joined)
            query = query.filter(models.ArtigoAvaliacaoModel.status.in_(["concluido", "Concluído"]))
        elif st_lower in ["pendente"]:
            query = query.filter(
                (models.ArtigoAvaliacaoModel.status.notin_(["concluido", "Concluído"])) | 
                (models.ArtigoAvaliacaoModel.status == None)
            )

    # 5. Paginação matemática
    total_registros = query.count()
    total_paginas = ceil(total_registros / size) if total_registros > 0 else 1
    
    if page < 1: page = 1
    if page > total_paginas: page = total_paginas
    
    offset = (page - 1) * size
    artigos_paginados = query.offset(offset).limit(size).all()

    # 6. Envia o contexto mapeado para o Jinja2
    return templates.TemplateResponse(
        "artigos_lista.html",
        {
            "request": request,
            "artigos": artigos_paginados,
            "idiomas_lista": idiomas_lista,
            "current_user": current_user,  
            "page": page,
            "size": size,
            "total_registros": total_registros,
            "total_paginas": total_paginas
        }
    )

