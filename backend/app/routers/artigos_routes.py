from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
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
    ano: Optional[str] = None,    
    db: Session = Depends(get_db)
):
    # 1. PEGA O USUÁRIO DIRETO DA SESSÃO (Alinhado com o seu core/auth.py)
    username_logado = request.session.get("user")
    
    # Criamos um objeto genérico mockado apenas para o HTML não quebrar ao ler current_user.username
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
        v_ano = form_data.get("ano", "")
        
        url_redirecionamento = f"/artigos/?page=1&size={size}&id={v_id}&codigo={v_codigo}&idioma={v_idioma}&ano={v_ano}"
        return RedirectResponse(url=url_redirecionamento, status_code=303)

    # --- FLUXO DO GET ---

    # 3. Busca os idiomas apenas dos artigos designados a este usuário para o <select>
    idiomas_lista = [
        r[0] for r in db.query(models.ArtigoModel.idioma)\
        .join(models.ArtigoAvaliacaoModel, models.ArtigoModel.id == models.ArtigoAvaliacaoModel.artigo_id)\
        .filter(models.ArtigoAvaliacaoModel.username == username_logado)\
        .distinct().all() if r[0]
    ]

    # 4. Construção da query trazendo apenas os artigos do usuário logado
    query = db.query(models.ArtigoModel)\
        .join(models.ArtigoAvaliacaoModel, models.ArtigoModel.id == models.ArtigoAvaliacaoModel.artigo_id)\
        .filter(models.ArtigoAvaliacaoModel.username == username_logado)
    
    if id and id.strip() != "":
        try: query = query.filter(models.ArtigoModel.id == int(id))
        except ValueError: pass 
            
    if codigo and codigo.strip() != "":
        query = query.filter(models.ArtigoModel.codigo.ilike(f"%{codigo}%"))
        
    if idioma and idioma.strip() != "":
        query = query.filter(models.ArtigoModel.idioma == idioma)
        
    if ano and ano.strip() != "":
        try: query = query.filter(models.ArtigoModel.ano_publicacao == int(ano))
        except ValueError: pass 

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