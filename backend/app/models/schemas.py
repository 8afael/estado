from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Exemplo para a Avaliação
class AvaliacaoCreate(BaseModel):
    usuario_id: int
    artigo_id: int
    etapa: int = Field(..., ge=1, le=3) # Garante valor entre 1 e 3
    t1_termos_chave: Optional[str] = None
    t2_contexto_publico: Optional[str] = None
    t3_tema_institucional: Optional[str] = None
    t4_analise_direta: Optional[str] = None
    resultado: Optional[str] = None
    usou_ia: Optional[str] = None
    ia_ferramentas_uso: Optional[str] = None
    ia_prompts: Optional[str] = None
    observacoes: Optional[str] = None

class AvaliacaoResponse(AvaliacaoCreate):
    id: int
    data_avaliacao: datetime

    class Config:
        # Permite que o Pydantic leia modelos do SQLAlchemy diretamente
        from_attributes = True