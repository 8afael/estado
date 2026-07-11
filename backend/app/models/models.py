from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, Text, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    salt = Column(String(32), nullable=False)

class ArtigoModel(Base):
    __tablename__ = "artigo"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, nullable=False)
    link = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    resumo = Column(String)
    ano_publicacao = Column(String)
    idioma = Column(String)
    paises_autores = Column(String)
    pais_estudado = Column(String)
    tipo_documento = Column(String)
    abordagem_metodologica = Column(String)

class AvaliacaoModel(Base):
    __tablename__ = "avaliacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    artigo_id = Column(Integer, ForeignKey("artigo.id", ondelete="CASCADE"), nullable=False)
    etapa = Column(Integer, nullable=False)

    codigo = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    
    resumo = Column(Text, nullable=False) 
    
    ano_publicacao = Column(Integer)
    idioma = Column(String)
    paises_autores = Column(String)
    pais_estudado = Column(String)
    tipo_documento = Column(String)
    abordagem_metodologica = Column(String)

    t1_termos_chave = Column(String)
    t2_contexto_publico = Column(String)
    t3_tema_institucional = Column(String)
    t4_analise_direta = Column(String)
    resultado = Column(String)
    
    usou_ia = Column(String)
    ia_ferramentas_uso = Column(String)
    ia_prompts = Column(String)
    observacoes = Column(String)
    data_avaliacao = Column(DateTime, server_default=func.now())

    artigo = relationship("ArtigoModel", backref="avaliacoes")
    
    # Restrições equivalentes ao SQL
    __table_args__ = (
        CheckConstraint("etapa IN (1, 2, 3)", name="check_etapa_valida"),
        UniqueConstraint("usuario_id", "artigo_id", "etapa", name="uq_usuario_artigo_etapa"),
    )

class ArtigoAvaliacaoModel(Base):
    __tablename__ = "artigo_avaliacoes"
    id = Column(Integer, primary_key=True, index=True)
    artigo_id = Column(Integer, ForeignKey("artigo.id"))
    username = Column(String)
    status = Column(String, default="pendente")

    artigo = relationship("ArtigoModel", backref="distribuicoes")