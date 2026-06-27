from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import hash_password
from app.models import crud
from app.models import models
from app.models import schemas
from app.core.auth import require_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/enquadramentos/novo", response_class=HTMLResponse)
@require_login
def novo_enquadramento(request: Request, db: Session = Depends(get_db)):
    enquadramentos = crud.get_enquadramentos(db)
    return templates.TemplateResponse(
        "enquadramentos/form.html",
        {
            "request": request,
            "enquadramento": None,
            "enquadramentos": enquadramentos
        }
    )

@router.post("/enquadramentos/novo")
@require_login
def criar_enquadramento(
    request: Request,
    descricao: str = Form(...),
    outro: str | None = Form(None),
    db: Session = Depends(get_db)
):
    crud.create_enquadramento(
        db,
        schemas.EnquadramentoCreate(
            descricao=descricao,
            outro=outro
        )
    )
    #return RedirectResponse("/enquadramentos", status_code=303)
    return RedirectResponse("/doutoramento/enquadramentos", status_code=303)

@router.get("/enquadramentos/{tid}/editar", response_class=HTMLResponse)
@require_login
def editar_enquadramento(
    request: Request,
    tid: int,
    db: Session = Depends(get_db)
):
    enquadramento = crud.get_enquadramento(db, tid)
    if not enquadramento:
        raise HTTPException(status_code=404, detail="Enquadramento não encontrado")

    return templates.TemplateResponse(
        "enquadramentos/form.html",
        {
            "request": request,
            "enquadramento": enquadramento
        }
    )

@router.post("/enquadramentos/{tid}/editar")
@require_login
def atualizar_enquadramento(
    request: Request,
    tid: int,
    descricao: str = Form(...),
    outro: str | None = Form(None),
    db: Session = Depends(get_db)
):
    schema = schemas.EnquadramentoUpdate(
        descricao=descricao,
        outro=outro
    )

    atualizado = crud.update_enquadramento(db, tid, schema)

    if not atualizado:
        raise HTTPException(status_code=404, detail="Enquadramento não encontrado")

    #return RedirectResponse("/enquadramentos", status_code=303)
    return RedirectResponse("/doutoramento/enquadramentos", status_code=303)

@router.get("/enquadramentos", response_class=HTMLResponse)
@require_login
def listar_enquadramentos(request: Request, db: Session = Depends(get_db)):
    enquadramentos = crud.get_enquadramentos(db)
    return templates.TemplateResponse(
        "enquadramentos/list.html",
        {"request": request, "enquadramentos": enquadramentos}
    )