import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from scipy import stats
import bd
# Imports das suas classes modulares
from graficos.analiseAutoria import AnaliseAutoria
from graficos.centralidade import Centralidade
from graficos.sazonalidade import Sazonalidade
from graficos.analiseAbrangencia import AnaliseAbrangencia
from graficos.analiseLinguagem import AnaliseLinguagem
from graficos.persuasao import AnalisePersuasao
from graficos.analisePersuasaoLinguagem import AnalisePersuasaoLinguagem
from graficos.lead import AnaliseLeadQuant
from graficos.enquadramento import AnaliseEnquadramento
from graficos.papelJornalistico import AnalisePapelJornalistico
from graficos.analiseTemas import AnaliseTemas
from graficos.analiseTemasEnquadramento import AnaliseCruzamentoTemasEnquadramento
from graficos.analiseTemasPapel import AnaliseTemasPapel
from graficos.analiseGenero import AnaliseGenero
from graficos.analiseFontes import AnaliseFontes
from graficos.analiseClimática import AnaliseClimatica
import dicionario
from graficos.aberturaDashboard import AberturaDashboard

# --- 1. CONFIGURAÇÕES VISUAIS E GLOBAIS ---
st.set_page_config(page_title="Dashboard Jornais", layout="wide")
pio.templates.default = "plotly_white"
bootstrap_colors = ["#0d6efd", "#6c757d", "#198754", "#dc3545", "#ffc107", "#0dcaf0"]

# Inicialização do Session State para Navegação
if 'pagina_ativa' not in st.session_state:
    st.session_state['pagina_ativa'] = "🏠 Home"

MESES_PT_MAPA = dicionario.MESES_PT_MAPA

# --- 2. FUNÇÃO DE CARGA E LIMPEZA DE DADOS ---
@st.cache_data
def load_data():
    # Ajuste o caminho conforme seu ambiente
    conn = sqlite3.connect(bd.BD)
    df = pd.read_sql("SELECT * FROM jornais", conn)
    conn.close()

    if 'pagina' in df.columns:
            df['pagina'] = df['pagina'].astype(str).replace('nan', '')
    
    df['dataPublicacao'] = pd.to_datetime(df['dataPublicacao'], errors='coerce')
    df = df.dropna(subset=['dataPublicacao'])
    
    df['Ano_Int'] = df['dataPublicacao'].dt.year
    df['Década'] = (df['Ano_Int'] // 10 * 10).astype(str) + "s"
    df['Mes_Num'] = df['dataPublicacao'].dt.month
    df['Mes_Nome'] = df['Mes_Num'].map(MESES_PT_MAPA)
    
    return df

try:
    df_original = load_data()
except Exception as e:
    st.error(f"Erro ao carregar o banco de dados: {e}")
    st.stop()

# --- 3. BARRA LATERAL (NAVEGAÇÃO E FILTROS) ---
st.sidebar.header("🧭 Navegação")

# Mapeamento de opções (Adicionado 🏠 Home)
opcoes_menu = {
    "🏠 Home": "home",
    "📊 Distribuição e Sazonalidade": "sazonalidade",
    "📝 Análise de Extensão (Centralidade)": "centralidade",
    "✍️ Perfil de Autoria": "autoria",
    "🌍 Abrangência Geográfica": "abrangencia",
    "🔡 Linguagem dos Títulos (Mesquita)": "linguagem",
    "🎯 Persuasão (Mesquita, 2022)": "persuasao",
    "🎯 Linguagem vs. Persuasão": "linguagemPersuasao",
    "📊 Análise Quantitativa dos Leads": "lead",
    "🖼️ Enquadramento Jornalístico Dominante": "enqDominante",
    "🎭 Papel Jornalístico Predominante (1973-2023)": "papJornalistico",
    "🌍 Análise de Temas": "temas",
    "📝 Temas vs. Enquadramento": "temasEnquadramento",
    "🔡 Temas vs Papel do Jornalismo": "papelJornalismo",
    "📊 Análise de Gênero": "genero",
    "📝 Análise de Fontes": "fontes",
    "🌍 Análise Climática": "climatica"
}

# Lógica para sincronizar Selectbox com Session State
lista_labels = list(opcoes_menu.keys())
index_default = lista_labels.index(st.session_state['pagina_ativa']) if st.session_state['pagina_ativa'] in lista_labels else 0

analise_selecionada = st.sidebar.selectbox(
    "Selecione a análise desejada:",
    lista_labels,
    index=index_default
)

# Atualiza o estado da página ao mudar o seletor
st.session_state['pagina_ativa'] = analise_selecionada

st.sidebar.divider()
st.sidebar.header("⚙️ Filtros")

min_db = df_original['dataPublicacao'].min().to_pydatetime()
max_db = df_original['dataPublicacao'].max().to_pydatetime()

datas_sel = st.sidebar.date_input(
    "Intervalo de datas", 
    value=(min_db, max_db), 
    min_value=min_db, 
    max_value=max_db, 
    format="DD/MM/YYYY"
)

# Filtro de dados global
df = df_original.copy()
if isinstance(datas_sel, tuple) and len(datas_sel) == 2:
    start_date, end_date = datas_sel
    df = df[(df['dataPublicacao'].dt.date >= start_date) & (df['dataPublicacao'].dt.date <= end_date)]

# --- 4. LÓGICA DE EXIBIÇÃO ---
# Chave interna da análise
chave_analise = opcoes_menu[analise_selecionada]

if chave_analise == "home":
    # Abertura utiliza o DF já filtrado por data
    abertura = AberturaDashboard(df)
    abertura.renderizar()

elif chave_analise == "sazonalidade":
    Sazonalidade(df, bootstrap_colors).renderizar()

elif chave_analise == "centralidade":
    Centralidade(df, bootstrap_colors).renderizar()

elif chave_analise == "autoria":
    AnaliseAutoria(df, bootstrap_colors).renderizar()

elif chave_analise == "abrangencia":
    AnaliseAbrangencia(df, bootstrap_colors).renderizar()

elif chave_analise == "linguagem":
    AnaliseLinguagem(df, bootstrap_colors).renderizar()

elif chave_analise == "persuasao":
    AnalisePersuasao(df, bootstrap_colors).renderizar()

elif chave_analise == "linguagemPersuasao":
    AnalisePersuasaoLinguagem(df, bootstrap_colors).renderizar()

elif chave_analise == "lead":
    AnaliseLeadQuant(df, bootstrap_colors).renderizar()

elif chave_analise == "enqDominante":
    AnaliseEnquadramento(df, bootstrap_colors).renderizar()

elif chave_analise == "papJornalistico":
    AnalisePapelJornalistico(df, bootstrap_colors).renderizar()

elif chave_analise == "temas":
    AnaliseTemas(df, bootstrap_colors).renderizar()

elif chave_analise == "temasEnquadramento":
    AnaliseCruzamentoTemasEnquadramento(df, bootstrap_colors).renderizar()

elif chave_analise == "papelJornalismo":
    AnaliseTemasPapel(df, bootstrap_colors).renderizar()

elif chave_analise == "genero":
    AnaliseGenero(df, bootstrap_colors).renderizar()

elif chave_analise == "fontes":
    AnaliseFontes(df, bootstrap_colors).renderizar()

elif chave_analise == "climatica":
    AnaliseClimatica(df, bootstrap_colors).renderizar()

# --- 5. TABELA FINAL ---
st.divider()
with st.expander("📄 Ver Dados Detalhados (Corpus Selecionado)"):
    df_display = df.copy()
    df_display['dataPublicacao'] = df_display['dataPublicacao'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_display, width='stretch')