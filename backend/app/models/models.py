from datetime import datetime

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
    nome_arquivo = Column(String)
    resultado_final = Column(String)

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

    decisao = Column(String)

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
    etapa = Column(Integer, nullable=False, default=2)

    artigo = relationship("ArtigoModel", backref="distribuicoes")


class Avaliacao3Model(Base):
    __tablename__ = "avaliacoes_3"
 
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    artigo_id = Column(Integer, ForeignKey("artigo.id", ondelete="CASCADE"), nullable=False)
    etapa = Column(Integer, nullable=False, default=2)
 
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

    decisao = Column(String)
 
    artigo = relationship("ArtigoModel", backref="avaliacoes_3")
 
    __table_args__ = (
        CheckConstraint("etapa = 2", name="check_etapa_avaliacao_3"),
        UniqueConstraint("artigo_id", name="uq_artigo_avaliacao_3"),
    )

class SnapshotDecisaoFinalModel(Base):
    __tablename__ = "snapshot_decisao_final"

    id = Column(Integer, primary_key=True, index=True)
    artigo_id = Column(Integer, index=True, unique=True, nullable=False)
    codigo = Column(String, nullable=True)
    titulo = Column(String, nullable=True)
    a1 = Column(String, nullable=True)
    a2 = Column(String, nullable=True)
    a3 = Column(String, nullable=True)
    decisao_final = Column(String, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, nullable=False)


class ExtracaoDadosModel(Base):
    __tablename__ = "extracao_dados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    artigo_id = Column(Integer, ForeignKey("artigo.id", ondelete="CASCADE"), nullable=False, unique=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Seção 1 — Identificação (Q1/Q2 não entram aqui, vêm de ArtigoModel)
    q3_referencia_bibliografica = Column(Text)
    q4_idioma = Column(String)
    q6_objetivo_principal = Column(Text)
    q6_loc = Column(String)

    # Seção 2 — Método
    q7_natureza_artigo = Column(String)
    q8_abordagem_metodologica = Column(String)
    q13_escala_geografica = Column(String)
    q15_descricao_unidade = Column(Text)
    q15_loc = Column(String)

    # Seção 3 — Conceitos
    q18_conceito_principal = Column(String)
    q19_definicao_textual = Column(Text)
    q19_loc = Column(String)
    q20_tipo_definicao = Column(String)
    q22_explicacao_delimitacao = Column(Text)
    q22_loc = Column(String)
    q23_relacao_governo_aberto = Column(String)
    q24_relacao_governanca_aberta = Column(String)
    q25_relacoes_pares_conceituais = Column(Text)
    q25_loc = Column(String)

    # Seção 4 — Princípios
    q27_apresenta_dimensoes = Column(String)
    q28_dimensoes_componentes = Column(Text)
    q28_loc = Column(String)

    # Seção 5 — Operacionalização
    q29_operacionalizado = Column(String)
    q32_descricao_operacionalizacao = Column(Text)
    q32_loc = Column(String)

    # Seção 6 — Instituições/tecnologia
    q36_especificacao_instrumentos = Column(Text)
    q36_loc = Column(String)
    q37_analisa_ferramentas_digitais = Column(String)

    # Seção 7 — Implementação
    q41_estagio_implementacao = Column(String)
    q46_extensao_mudanca = Column(String)
    q47_evidencia_mudanca_poder = Column(String)

    # Seção 9 — Síntese
    q50_contribuicao_conceitual = Column(Text)
    q50_loc = Column(String)
    q51_contribuicao_empirica = Column(Text)
    q51_loc = Column(String)
    q52_principal_tese = Column(Text)
    q52_loc = Column(String)
    q53_contributo_quadro_conceitual = Column(Text)
    q53_loc = Column(String)
    q54_limitacoes_lacunas = Column(Text)

    # Seção 10 — Qualidade/auditoria
    q55_clareza_artigo = Column(String)
    q56_confianca_codificacao = Column(String)
    q57_observacoes = Column(Text)
    q58_uso_ia = Column(String)
    q59_ferramenta_finalidade_prompt = Column(Text)

    status = Column(String, nullable=False, default="em_andamento")
    data_criacao = Column(DateTime, server_default=func.now())
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())

    artigo = relationship("ArtigoModel", backref="extracao_dados")
    multivalores = relationship(
        "ExtracaoMultivaloresModel",
        backref="extracao",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    outros = relationship(
        "ExtracaoOutrosModel",
        backref="extracao",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ExtracaoMultivaloresModel(Base):
    __tablename__ = "extracao_multivalores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    extracao_id = Column(Integer, ForeignKey("extracao_dados.id", ondelete="CASCADE"), nullable=False)
    campo = Column(String, nullable=False)   # ex: 'q9', 'q26', 'q5_paises'
    valor = Column(String, nullable=False)


class ExtracaoOutrosModel(Base):
    __tablename__ = "extracao_outros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    extracao_id = Column(Integer, ForeignKey("extracao_dados.id", ondelete="CASCADE"), nullable=False)
    campo = Column(String, nullable=False)   # ex: 'q4', 'q9', 'q18'
    texto = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("extracao_id", "campo", name="uq_extracao_outros_campo"),
    )