from sqlalchemy.orm import Session
from app.models import models
from app.models import schemas

def criar_avaliacao(db: Session, avaliacao: schemas.AvaliacaoCreate):
    # Transforma o schema Pydantic em Model do SQLAlchemy
    db_avaliacao = models.AvaliacaoModel(**avaliacao.model_dump())
    db.add(db_avaliacao)
    db.commit()
    db.refresh(db_avaliacao)
    return db_avaliacao

def obter_avaliacoes_por_artigo(db: Session, artigo_id: int):
    return db.query(models.AvaliacaoModel).filter(models.AvaliacaoModel.artigo_id == artigo_id).all()