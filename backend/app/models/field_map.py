"""
Mapeamento único entre as perguntas do formulário HTML (Q1..Q59) e o
destino de cada uma no banco de dados.

Este módulo é a fonte de verdade para:
  - schemas.py        (o que entra no payload Pydantic e como)
  - extracao_service.py (como o payload é gravado/lido no banco)

Cada entrada descreve:
  - tipo: "single" | "multi" | "long" | "scale" | "country"
  - coluna: nome da coluna em ExtracaoDadosModel, ou None se o valor
            vive só em extracao_multivalores (campo EAV)
  - loc_coluna: nome da coluna "<qN>_loc" quando o form tem o campo de
                localização/evidência associado, senão None
  - eav_campo: valor gravado em extracao_multivalores.campo quando o
               tipo é "multi" (ou "country"), senão None
  - tem_outro: True se o form tem opção "Outro/Outra — especificar"
               para essa pergunta (grava em extracao_outros)

Perguntas Q1/Q2 (id do estudo, nome do arquivo) ficam de fora: são
preenchidas automaticamente a partir de ArtigoModel e não pertencem à
extração.

IMPORTANTE: se você adicionar/mudar uma pergunta no HTML, atualize
este dicionário primeiro — schemas e service leem só daqui, não têm
nenhuma lista de perguntas hardcoded em paralelo.
"""

FIELD_MAP = {
    # ---- Seção 1 — Identificação ----
    "q3":  {"tipo": "long",   "coluna": "q3_referencia_bibliografica", "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q4":  {"tipo": "single", "coluna": "q4_idioma",                   "loc_coluna": None,   "eav_campo": None,  "tem_outro": True},
    "q5":  {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q5",  "tem_outro": False},
    "q5_paises": {"tipo": "country", "coluna": None,                  "loc_coluna": None,   "eav_campo": "q5_paises", "tem_outro": False},
    "q6":  {"tipo": "long",   "coluna": "q6_objetivo_principal",       "loc_coluna": "q6_loc", "eav_campo": None, "tem_outro": False},

    # ---- Seção 2 — Método, desenho, fase ----
    "q7":  {"tipo": "single", "coluna": "q7_natureza_artigo",          "loc_coluna": None,   "eav_campo": None,  "tem_outro": True},
    "q8":  {"tipo": "single", "coluna": "q8_abordagem_metodologica",   "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q9":  {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q9",  "tem_outro": True},
    "q10": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q10", "tem_outro": True},
    "q11": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q11", "tem_outro": True},
    "q12": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q12", "tem_outro": False},
    "q13": {"tipo": "single", "coluna": "q13_escala_geografica",       "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q14": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q14", "tem_outro": True},
    "q15": {"tipo": "long",   "coluna": "q15_descricao_unidade",       "loc_coluna": "q15_loc", "eav_campo": None, "tem_outro": False},

    # ---- Seção 3 — Conceitos e definição ----
    "q16": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q16", "tem_outro": True},
    "q17": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q17", "tem_outro": True},
    "q18": {"tipo": "single", "coluna": "q18_conceito_principal",      "loc_coluna": None,   "eav_campo": None,  "tem_outro": True},
    "q19": {"tipo": "long",   "coluna": "q19_definicao_textual",       "loc_coluna": "q19_loc", "eav_campo": None, "tem_outro": False},
    "q20": {"tipo": "single", "coluna": "q20_tipo_definicao",          "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q21": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q21", "tem_outro": False},
    "q22": {"tipo": "long",   "coluna": "q22_explicacao_delimitacao",  "loc_coluna": "q22_loc", "eav_campo": None, "tem_outro": False},
    "q23": {"tipo": "single", "coluna": "q23_relacao_governo_aberto",  "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q24": {"tipo": "single", "coluna": "q24_relacao_governanca_aberta", "loc_coluna": None, "eav_campo": None,  "tem_outro": False},
    "q25": {"tipo": "long",   "coluna": "q25_relacoes_pares_conceituais", "loc_coluna": "q25_loc", "eav_campo": None, "tem_outro": False},

    # ---- Seção 4 — Princípios e dimensões normativas ----
    "q26": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q26", "tem_outro": True},
    "q27": {"tipo": "single", "coluna": "q27_apresenta_dimensoes",     "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q28": {"tipo": "long",   "coluna": "q28_dimensoes_componentes",   "loc_coluna": "q28_loc", "eav_campo": None, "tem_outro": False},

    # ---- Seção 5 — Operacionalização ----
    "q29": {"tipo": "single", "coluna": "q29_operacionalizado",        "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q30": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q30", "tem_outro": True},
    "q31": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q31", "tem_outro": True},
    "q32": {"tipo": "long",   "coluna": "q32_descricao_operacionalizacao", "loc_coluna": "q32_loc", "eav_campo": None, "tem_outro": False},

    # ---- Seção 6 — Instituições, direito e tecnologia ----
    "q33": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q33", "tem_outro": True},
    "q34": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q34", "tem_outro": False},
    "q35": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q35", "tem_outro": True},
    "q36": {"tipo": "long",   "coluna": "q36_especificacao_instrumentos", "loc_coluna": "q36_loc", "eav_campo": None, "tem_outro": False},
    "q37": {"tipo": "single", "coluna": "q37_analisa_ferramentas_digitais", "loc_coluna": None, "eav_campo": None, "tem_outro": False},
    "q38": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q38", "tem_outro": True},
    "q39": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q39", "tem_outro": True},
    "q40": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q40", "tem_outro": False},

    # ---- Seção 7 — Implementação, obstáculos e efeitos ----
    "q41": {"tipo": "single", "coluna": "q41_estagio_implementacao",   "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q42": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q42", "tem_outro": True},
    "q43": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q43", "tem_outro": True},
    "q44": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q44", "tem_outro": True},
    "q45": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q45", "tem_outro": True},
    "q46": {"tipo": "single", "coluna": "q46_extensao_mudanca",        "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q47": {"tipo": "single", "coluna": "q47_evidencia_mudanca_poder", "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},

    # ---- Seção 8 — Sociedade civil e mídia ----
    "q48": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q48", "tem_outro": True},
    "q49": {"tipo": "multi",  "coluna": None,                          "loc_coluna": None,   "eav_campo": "q49", "tem_outro": True},

    # ---- Seção 9 — Síntese analítica ----
    "q50": {"tipo": "long",   "coluna": "q50_contribuicao_conceitual", "loc_coluna": "q50_loc", "eav_campo": None, "tem_outro": False},
    "q51": {"tipo": "long",   "coluna": "q51_contribuicao_empirica",   "loc_coluna": "q51_loc", "eav_campo": None, "tem_outro": False},
    "q52": {"tipo": "long",   "coluna": "q52_principal_tese",          "loc_coluna": "q52_loc", "eav_campo": None, "tem_outro": False},
    "q53": {"tipo": "long",   "coluna": "q53_contributo_quadro_conceitual", "loc_coluna": "q53_loc", "eav_campo": None, "tem_outro": False},
    "q54": {"tipo": "long",   "coluna": "q54_limitacoes_lacunas",      "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},

    # ---- Seção 10 — Qualidade e auditoria ----
    "q55": {"tipo": "scale",  "coluna": "q55_clareza_artigo",          "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q56": {"tipo": "single", "coluna": "q56_confianca_codificacao",   "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q57": {"tipo": "long",   "coluna": "q57_observacoes",             "loc_coluna": None,   "eav_campo": None,  "tem_outro": False},
    "q58": {"tipo": "single", "coluna": "q58_uso_ia",                  "loc_coluna": None,   "eav_campo": None,  "tem_outro": True},
    "q59": {"tipo": "long",   "coluna": "q59_ferramenta_finalidade_prompt", "loc_coluna": None, "eav_campo": None, "tem_outro": False},
}

# Perguntas cujo tipo grava em extracao_multivalores (multi-select "de verdade")
MULTI_FIELDS = [q for q, m in FIELD_MAP.items() if m["tipo"] in ("multi", "country")]

# Perguntas com opção "Outro — especificar" -> gravam em extracao_outros
OTHER_FIELDS = [q for q, m in FIELD_MAP.items() if m["tem_outro"]]

# Perguntas com coluna direta em ExtracaoDadosModel
DIRECT_COLUMN_FIELDS = {q: m["coluna"] for q, m in FIELD_MAP.items() if m["coluna"]}

# Perguntas com coluna de localização/evidência (<qN>_loc)
LOC_COLUMN_FIELDS = {q: m["loc_coluna"] for q, m in FIELD_MAP.items() if m["loc_coluna"]}