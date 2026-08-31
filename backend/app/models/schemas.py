from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict
from datetime import datetime
from app.models.field_map import FIELD_MAP, MULTI_FIELDS, OTHER_FIELDS

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


class ExtracaoDadosCreate(BaseModel):
    """
    Payload recebido do formulário. Os campos "single"/"long"/"scale" viram
    atributos normais (Optional[str]); os campos "multi" e "country" viram
    List[str]; e cada pergunta com "Outro — especificar" ganha um campo
    irmão "<qN>_outro".
 
    Este schema é o único ponto em que o payload do front é validado antes
    de ser explodido em ExtracaoDadosModel / ExtracaoMultivaloresModel /
    ExtracaoOutrosModel pelo extracao_service.
    """
 
    artigo_id: int
    usuario_id: int
 
    # ---- Seção 1 ----
    q3_referencia_bibliografica: Optional[str] = None
    q4_idioma: Optional[str] = None
    q4_outro: Optional[str] = None
    q5: List[str] = Field(default_factory=list)
    q5_paises: List[str] = Field(default_factory=list)
    q6_objetivo_principal: Optional[str] = None
    q6_loc: Optional[str] = None
 
    # ---- Seção 2 ----
    q7_natureza_artigo: Optional[str] = None
    q7_outro: Optional[str] = None
    q8_abordagem_metodologica: Optional[str] = None
    q9: List[str] = Field(default_factory=list)
    q9_outro: Optional[str] = None
    q10: List[str] = Field(default_factory=list)
    q10_outro: Optional[str] = None
    q11: List[str] = Field(default_factory=list)
    q11_outro: Optional[str] = None
    q12: List[str] = Field(default_factory=list)
    q13_escala_geografica: Optional[str] = None
    q14: List[str] = Field(default_factory=list)
    q14_outro: Optional[str] = None
    q15_descricao_unidade: Optional[str] = None
    q15_loc: Optional[str] = None
 
    # ---- Seção 3 ----
    q16: List[str] = Field(default_factory=list)
    q16_outro: Optional[str] = None
    q17: List[str] = Field(default_factory=list)
    q17_outro: Optional[str] = None
    q18_conceito_principal: Optional[str] = None
    q18_outro: Optional[str] = None
    q19_definicao_textual: Optional[str] = None
    q19_loc: Optional[str] = None
    q20_tipo_definicao: Optional[str] = None
    q21: List[str] = Field(default_factory=list)
    q22_explicacao_delimitacao: Optional[str] = None
    q22_loc: Optional[str] = None
    q23_relacao_governo_aberto: Optional[str] = None
    q24_relacao_governanca_aberta: Optional[str] = None
    q25_relacoes_pares_conceituais: Optional[str] = None
    q25_loc: Optional[str] = None
 
    # ---- Seção 4 ----
    q26: List[str] = Field(default_factory=list)
    q26_outro: Optional[str] = None
    q27_apresenta_dimensoes: Optional[str] = None
    q28_dimensoes_componentes: Optional[str] = None
    q28_loc: Optional[str] = None
 
    # ---- Seção 5 ----
    q29_operacionalizado: Optional[str] = None
    q30: List[str] = Field(default_factory=list)
    q30_outro: Optional[str] = None
    q31: List[str] = Field(default_factory=list)
    q31_outro: Optional[str] = None
    q32_descricao_operacionalizacao: Optional[str] = None
    q32_loc: Optional[str] = None
 
    # ---- Seção 6 ----
    q33: List[str] = Field(default_factory=list)
    q33_outro: Optional[str] = None
    q34: List[str] = Field(default_factory=list)
    q35: List[str] = Field(default_factory=list)
    q35_outro: Optional[str] = None
    q36_especificacao_instrumentos: Optional[str] = None
    q36_loc: Optional[str] = None
    q37_analisa_ferramentas_digitais: Optional[str] = None
    q38: List[str] = Field(default_factory=list)
    q38_outro: Optional[str] = None
    q39: List[str] = Field(default_factory=list)
    q39_outro: Optional[str] = None
    q40: List[str] = Field(default_factory=list)
 
    # ---- Seção 7 ----
    q41_estagio_implementacao: Optional[str] = None
    q42: List[str] = Field(default_factory=list)
    q42_outro: Optional[str] = None
    q43: List[str] = Field(default_factory=list)
    q43_outro: Optional[str] = None
    q44: List[str] = Field(default_factory=list)
    q44_outro: Optional[str] = None
    q45: List[str] = Field(default_factory=list)
    q45_outro: Optional[str] = None
    q46_extensao_mudanca: Optional[str] = None
    q47_evidencia_mudanca_poder: Optional[str] = None
 
    # ---- Seção 8 ----
    q48: List[str] = Field(default_factory=list)
    q48_outro: Optional[str] = None
    q49: List[str] = Field(default_factory=list)
    q49_outro: Optional[str] = None
 
    # ---- Seção 9 ----
    q50_contribuicao_conceitual: Optional[str] = None
    q50_loc: Optional[str] = None
    q51_contribuicao_empirica: Optional[str] = None
    q51_loc: Optional[str] = None
    q52_principal_tese: Optional[str] = None
    q52_loc: Optional[str] = None
    q53_contributo_quadro_conceitual: Optional[str] = None
    q53_loc: Optional[str] = None
    q54_limitacoes_lacunas: Optional[str] = None
 
    # ---- Seção 10 ----
    q55_clareza_artigo: Optional[str] = None
    q56_confianca_codificacao: Optional[str] = None
    q57_observacoes: Optional[str] = None
    q58_uso_ia: Optional[str] = None
    q58_outro: Optional[str] = None
    q59_ferramenta_finalidade_prompt: Optional[str] = None
 
    status: str = "em_andamento"
 
    @model_validator(mode="after")
    def _valida_outros_orfaos(self):
        """
        Um campo '<qN>_outro' só faz sentido se a opção "Outro —
        especificar" foi de fato marcada em qN. Evita gravar um texto de
        especificação órfão em extracao_outros.
        """
        for q in OTHER_FIELDS:
            outro_valor = getattr(self, f"{q}_outro", None)
            if not outro_valor:
                continue
            campo_meta = FIELD_MAP[q]
            if campo_meta["tipo"] == "multi":
                selecionado = getattr(self, q, [])
                marcou_outro = any("especificar" in v.lower() for v in selecionado)
            else:
                valor_single = getattr(self, campo_meta["coluna"], None) if campo_meta["coluna"] else None
                marcou_outro = bool(valor_single and "especificar" in valor_single.lower())
            if not marcou_outro:
                raise ValueError(
                    f"'{q}_outro' foi preenchido mas a opção 'Outro — especificar' "
                    f"não foi selecionada em {q}."
                )
        return self
 
 
class ExtracaoDadosUpdate(ExtracaoDadosCreate):
    """Mesma forma do Create; usado em PATCH/PUT para salvar rascunho parcial."""
    artigo_id: Optional[int] = None
    usuario_id: Optional[int] = None
 
 
class ExtracaoDadosResponse(BaseModel):
    """
    Formato de leitura: reconstitui os campos multi (List[str]) e os
    "outro" a partir das tabelas EAV, além das colunas diretas.
    Montado pelo extracao_service.montar_response(), não direto do ORM,
    por isso não usa from_attributes.
    """
 
    id: int
    artigo_id: int
    usuario_id: int
    status: str
    data_criacao: datetime
    data_atualizacao: datetime
 
    campos: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Todas as colunas diretas (single/long/scale), por nome de coluna.",
    )
    multivalores: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Todas as respostas multi-select, por qN (inclui q5_paises).",
    )
    outros: Dict[str, str] = Field(
        default_factory=dict,
        description="Todos os textos de 'Outro — especificar', por qN.",
    )
 
    class Config:
        from_attributes = True