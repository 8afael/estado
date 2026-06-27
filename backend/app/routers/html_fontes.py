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

@router.get("/fontes", response_class=HTMLResponse)
@require_login
def listar_fontes(request: Request, db: Session = Depends(get_db)):
    fontes = crud.get_fontes(db)
    return templates.TemplateResponse(
        "fontes/list.html",
        {"request": request, "fontes": fontes}
    )

@router.get("/fontes/novo", response_class=HTMLResponse)
@require_login
def nova_fonte(request: Request, db: Session = Depends(get_db)):
    fontes = crud.get_fontes(db)
    return templates.TemplateResponse(
        "fontes/form.html",
        {
            "request": request,
            "fonte": None,
            "fontes": fontes
        }
    )

@router.post("/fontes/novo")
@require_login
def criar_fonte(
    request: Request,
    descricao: str = Form(...),
    outro: str | None = Form(None),
    db: Session = Depends(get_db)
):
    crud.create_fonte(
        db,
        schemas.FonteCreate(
            descricao=descricao,
            outro=outro
        )
    )
    #return RedirectResponse("/fontes", status_code=303)
    return RedirectResponse("/doutoramento/fontes", status_code=303)

@router.get("/fontes/{tid}/editar", response_class=HTMLResponse)
@require_login
def editar_tema(
    request: Request,
    tid: int,
    db: Session = Depends(get_db)
):
    fonte = crud.get_fonte(db, tid)
    if not fonte:
        raise HTTPException(status_code=404, detail="Fonte não encontrado")

    return templates.TemplateResponse(
        "fontes/form.html",
        {
            "request": request,
            "fonte": fonte
        }
    )

@router.post("/fontes/{tid}/editar")
@require_login
def atualizar_fonte(
    request: Request,
    tid: int,
    descricao: str = Form(...),
    outro: str | None = Form(None),
    db: Session = Depends(get_db)
):
    schema = schemas.FonteUpdate(
        descricao=descricao,
        outro=outro
    )

    atualizado = crud.update_fonte(db, tid, schema)

    if not atualizado:
        raise HTTPException(status_code=404, detail="Fonte não encontrado")

    #return RedirectResponse("/fontes", status_code=303)
    return RedirectResponse("/doutoramento/fontes", status_code=303)