from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.auth import require_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
@require_login
async def dashboard(request: Request):
    # Recupera o usuário da sessão
    user = request.session.get("user")
    
    # Renderiza o template passando o caminho relativo à pasta base definida no Jinja2Templates
    return templates.TemplateResponse(
        "dashboard/principal.html", 
        {
            "request": request, 
            "user": user
        }
    )
    
