from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.auth import require_login
from app.core.database import get_db
from app.core.auth import hash_password
from app.models import crud
from app.models import models
from app.models import schemas

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/temas/{tid}/editar", response_class=HTMLResponse)
@require_login
def editar_tema(
    tid: int,
    request: Request,
    db: Session = Depends(get_db)
):
    tema = crud.get_tema(db, tid)
    if not tema:
        raise HTTPException(status_code=404, detail="Tema não encontrado")

    return templates.TemplateResponse(
        "temas/form.html",
        {
            "request": request,
            "tema": tema
        }
    )

@router.post("/temas/{tid}/editar")
@require_login
def atualizar_tema(
    request: Request,
    tid: int,
    descricao: str = Form(...),
    outro: str | None = Form(None),
    db: Session = Depends(get_db)
):
    schema = schemas.TemaUpdate(
        descricao=descricao,
        outro=outro
    )

    atualizado = crud.update_tema(db, tid, schema)

    if not atualizado:
        raise HTTPException(status_code=404, detail="Tema não encontrado")

    return RedirectResponse("/doutoramento/temas", status_code=303)

@router.post("/temas/novo")
@require_login
def criar_tema(
    request: Request,
    descricao: str = Form(...),
    outro: str | None = Form(None),
    db: Session = Depends(get_db)
):
    crud.create_tema(
        db,
        schemas.TemaCreate(
            descricao=descricao,
            outro=outro
        )
    )
    return RedirectResponse("/doutoramento/temas", status_code=303)

@router.get("/temas/novo", response_class=HTMLResponse)
@require_login
def novo_tema(request: Request, db: Session = Depends(get_db)):
    temas = crud.get_temas(db)
    return templates.TemplateResponse(
        "temas/form.html",
        {
            "request": request,
            "tema": None,
            "temas": temas
        }
    )

@router.get("/temas", response_class=HTMLResponse)
@require_login
def listar_temas(request: Request, db: Session = Depends(get_db)):
    temas = crud.get_temas(db)
    return templates.TemplateResponse(
        "temas/list.html",
        {"request": request, "temas": temas}
    )