from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_password
from app.models import models

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/login/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}
    )

@router.post("/login/")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Usuário não encontrado"
            },
            status_code=400
        )

    if not verify_password(password, user.salt, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Senha incorreta"
            },
            status_code=400
        )

    request.session["user"] = user.username
    return RedirectResponse("/estado/artigos/", status_code=302)


# --- Logout ---
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/estado/login/", status_code=302)

