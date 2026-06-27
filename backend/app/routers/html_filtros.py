from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.core import database
from app.models import models
from app.models import crud

# Criamos o roteador específico para os filtros
router = APIRouter()

templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/filtros", response_class=HTMLResponse)
def filtrar_avaliacoes(
    request: Request, 
    etapa: Optional[int] = None, 
    resultado: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.AvaliacaoModel)
    
    if etapa:
        query = query.filter(models.AvaliacaoModel.etapa == etapa)
    if resultado:
        query = query.filter(models.AvaliacaoModel.resultado == resultado)
        
    avaliacoes_filtradas = query.all()
    
    return templates.TemplateResponse(
        "filtros.html", 
        {
            "request": request, 
            "avaliacoes": avaliacoes_filtradas, 
            "etapa_atual": etapa, 
            "resultado_atual": resultado
        }
    )