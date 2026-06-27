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

@router.get("/api/fontes", response_model=List[schemas.FonteRead])
def api_listar_fontes(db: Session = Depends(get_db)):
    return crud.get_fontes(db)

@router.post("/api/fontes", response_model=schemas.FonteRead)
def api_criar_fonte(data: schemas.FonteCreate, db: Session = Depends(get_db)):
    return crud.create_fonte(db, data)

@router.put("/api/fontes/{fid}", response_model=schemas.FonteRead)
def api_editar_fonte(
    fid: int,
    data: schemas.FonteUpdate,
    db: Session = Depends(get_db)
):
    obj = crud.update_fonte(db, fid, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    return obj

@router.delete("/api/fontes/{fid}")
def api_apagar_fonte(fid: int, db: Session = Depends(get_db)):
    ok = crud.delete_fonte(db, fid)
    if not ok:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    return {"success": True}