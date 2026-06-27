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

@router.get("/api/enquadramentos", response_model=List[schemas.EnquadramentoRead])
def api_listar_enquadramentos(db: Session = Depends(get_db)):
    return crud.get_enquadramentos(db)

@router.post("/api/enquadramentos", response_model=schemas.EnquadramentoRead)
def api_criar_enquadramento(
    data: schemas.EnquadramentoCreate,
    db: Session = Depends(get_db)
):
    return crud.create_enquadramento(db, data)

@router.put("/api/enquadramentos/{eid}", response_model=schemas.EnquadramentoRead)
def api_editar_enquadramento(
    eid: int,
    data: schemas.EnquadramentoUpdate,
    db: Session = Depends(get_db)
):
    obj = crud.update_enquadramento(db, eid, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Enquadramento não encontrado")
    return obj

@router.delete("/api/enquadramentos/{eid}")
def api_apagar_enquadramento(eid: int, db: Session = Depends(get_db)):
    ok = crud.delete_enquadramento(db, eid)
    if not ok:
        raise HTTPException(status_code=404, detail="Enquadramento não encontrado")
    return {"success": True}