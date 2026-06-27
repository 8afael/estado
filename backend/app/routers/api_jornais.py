from typing import List
from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import hash_password
from app.models import crud
from app.models import models
from app.models import schemas

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_model=List[schemas.JornalRead])
def api_listar_jornais(db: Session = Depends(get_db)):
    return crud.get_jornais(db)

@router.get("/{jid}", response_model=schemas.JornalRead)
def api_obter_jornal(jid: int, db: Session = Depends(get_db)):
    obj = crud.get_jornal(db, jid)
    if not obj:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")
    return obj

@router.post("/", response_model=schemas.JornalRead)
def api_criar_jornal(data: schemas.JornalCreate, db: Session = Depends(get_db)):
    return crud.create_jornal(db, data)

@router.put("/{jid}", response_model=schemas.JornalRead)
def api_editar_jornal(
    jid: int,
    data: schemas.JornalUpdate,
    db: Session = Depends(get_db)
):
    obj = crud.update_jornal(db, jid, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")
    return obj

@router.delete("/{jid}")
def api_apagar_jornal(jid: int, db: Session = Depends(get_db)):
    ok = crud.delete_jornal(db, jid)
    if not ok:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")
    return {"success": True}