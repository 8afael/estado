from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core import database
from app.core.auth import require_login
from app.models import models

# Roteador com prefixo /avaliacoes (combinado com o root_path="/estado", a rota HTML final será /estado/avaliacoes/resultados/)
router = APIRouter()

# Configuração do Jinja2 apontando para a pasta de templates
templates = Jinja2Templates(directory="app/templates")

@router.get("/regras/", response_class=HTMLResponse)
@require_login
async def exibir_regras(request: Request):

    username_logado = request.session.get("user")
    
    class UsuarioSessao:
        def __init__(self, username):
            self.username = username

    current_user = UsuarioSessao(username_logado)

    return templates.TemplateResponse(
        "regras_triagem.html",
        {
            "request": request,
            "current_user": current_user
        }
    )