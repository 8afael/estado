from typing import List
from fastapi import APIRouter, FastAPI, HTTPException, Request, Form, Depends
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

@router.get("/api/temas", response_model=List[schemas.TemaRead])
def api_listar_temas(db: Session = Depends(get_db)):
    return crud.get_temas(db)

@router.post("/api/temas", response_model=schemas.TemaRead)
def api_criar_tema(data: schemas.TemaCreate, db: Session = Depends(get_db)):
    return crud.create_tema(db, data)

@router.put("/api/temas/{tema_id}", response_model=schemas.TemaRead)
def api_editar_tema(
    tema_id: int,
    data: schemas.TemaUpdate,
    db: Session = Depends(get_db)
):
    obj = crud.update_tema(db, tema_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    return obj

@router.delete("/api/temas/{tema_id}")
def api_apagar_tema(tema_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_tema(db, tema_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    return {"success": True}
