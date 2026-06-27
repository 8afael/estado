import plotly.express as px
import streamlit as st
import dicionario
#from app.dashboard.cores from graficos import cores_JORNAIS
from graficos import cores

class AberturaDashboard:
    def __init__(self, df_selecionado):
        # Limpeza inicial: remove nulos das colunas base da hierarquia
        self.df = df_selecionado.dropna(subset=['jornal', 'genero'])
        self.df = self.df[(self.df['jornal'] != "") & (self.df['genero'] != "")]

    def renderizar(self):
        st.header("🔭 Panorama Geral do Corpus")
        
        # Mapeamento de Labels para as colunas reais do Banco de Dados
        opcoes_analise = {
            "Gênero": "genero",
            "Seção": "secao",
            "Autoria": "autoria",
            "Abrangência": "abrangencia",
            "Linguagem": "linguagem",
            "Enunciador": "enunciador",
            "Persuasão": "persuasao",
            "Lead": "lead",
            "Enquadramento Dominante": "enqDominante",
            "Enquadramento Eficácia": "enqEficacia",
            "Enquadramento Ação": "enqAcao",
            "Papel Jornalístico": "papJornalistico",
            "Alterações Climáticas": "climaticas"
        }
        
        colunas_disponiveis = {k: v for k, v in opcoes_analise.items() if v in self.df.columns}
        
        c1, _ = st.columns([0.4, 0.6])
        with c1:
            label_selecionado = st.selectbox(
                "Selecione a categoria para detalhar:",
                options=list(colunas_disponiveis.keys())
            )
        
        coluna_alvo = colunas_disponiveis[label_selecionado]
        df_view = self.df.copy()

        # 1. Limpeza rigorosa da coluna selecionada
        df_view = df_view.dropna(subset=[coluna_alvo])
        df_view = df_view[df_view[coluna_alvo].astype(str).str.strip() != ""]
        
        # 2. Lógica de Mapeamento Dinâmico via dicionario.py
        # Tentamos encontrar o mapa específico, ex: MAPA_ABRANGENCIA, MAPA_SECAO, etc.
        nome_mapa_esperado = "MAPA"
        
        # O Gênero é uma exceção pois seu dicionário costuma se chamar apenas 'MAPA'
        if coluna_alvo == 'genero':
            mapa_atual = getattr(dicionario, 'MAPA', {})
        else:
            mapa_atual = getattr(dicionario, nome_mapa_esperado, {})

        # Aplicar a tradução se o mapa existir, caso contrário mantém o original
        df_view[label_selecionado] = df_view[coluna_alvo].apply(
            lambda x: mapa_atual.get(x, x) if isinstance(mapa_atual, dict) else x
        )

        # 3. Agrupamento para o Sunburst
        df_agrupado = df_view.groupby(['jornal', label_selecionado]).size().reset_index(name='Total')

        # 4. Gráfico Sunburst
        fig_sun = px.sunburst(
            df_agrupado,
            path=['jornal', label_selecionado], 
            values='Total',
            color='jornal',
            color_discrete_map=cores.CORES_JORNAIS,
            title=f"Distribuição: Jornal > {label_selecionado}"
        )

        fig_sun.update_traces(
            textinfo="label+percent entry",
            hovertemplate='<b>%{label}</b><br>Qtd: %{value}<br>% no Jornal: %{percentEntry:.1%}'
        )

        fig_sun.update_layout(margin=dict(t=40, l=0, r=0, b=0), height=600)
        st.plotly_chart(fig_sun, width='stretch')
