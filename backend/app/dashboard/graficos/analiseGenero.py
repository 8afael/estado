import plotly.express as px
import streamlit as st
import pandas as pd
import dicionario
from graficos import cores

class AnaliseGenero:
    def __init__(self, df_selecionado, colors):
        self.df = df_selecionado
        self.colors = colors

    def renderizar(self):
        st.header("🎭 Distribuição por Gênero Jornalístico")

        # Verificação de segurança para as colunas
        if 'genero' not in self.df.columns or 'jornal' not in self.df.columns:
            st.error("Colunas 'genero' ou 'jornal' não encontradas.")
            return

        # 1. Preparação dos dados
        df_genero = self.df.copy()
        df_genero['genero_mapeado'] = df_genero['genero'].apply(lambda x: dicionario.MAPA.get(x, x))

        # Contagem Global (para a Tab 1)
        contagem_total = df_genero['genero_mapeado'].value_counts().reset_index()
        contagem_total.columns = ['Gênero', 'Quantidade']

        # Contagem por Jornal (para a Tab 2)
        contagem_jornal = df_genero.groupby(['genero_mapeado', 'jornal']).size().reset_index(name='Quantidade')

        # 2. KPIs rápidos
        c1, c2, c3 = st.columns(3)
        c1.metric("Gênero Predominante", contagem_total.iloc[0]['Gênero'])
        c2.metric("Total de Matérias", contagem_total['Quantidade'].sum())
        c3.metric("Qtd. de Jornais", self.df['jornal'].nunique())

        st.divider()

        # 3. Visualização em Abas
        tab_total, tab_por_jornal, tab_pizza = st.tabs([
            "📊 Frequência Total", 
            "📰 Distribuído por Jornal", 
            "🍕 Proporção %"
        ])

        with tab_total:
            fig_total = px.bar(
                contagem_total, 
                x='Quantidade', 
                y='Gênero', 
                orientation='h',
                text='Quantidade',
                title="Frequência Absoluta (Geral)",
                color_discrete_sequence=[self.colors[0] if self.colors else '#636EFA']
            )
            fig_total.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_total, width='stretch')

        with tab_por_jornal:
            fig_jornal = px.bar(
                contagem_jornal, 
                x='Quantidade', 
                y='genero_mapeado', 
                color='jornal',
                orientation='h',
                barmode='group', # 'group' para barras lado a lado, 'stack' para empilhadas
                title="Frequência de Gêneros por Jornal",
                labels={'genero_mapeado': 'Gênero', 'jornal': 'Jornal'},
                color_discrete_map=cores.CORES_JORNAIS
            )
            fig_jornal.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_jornal, width='stretch')

        with tab_pizza:
            fig_pie = px.pie(
                contagem_total, 
                values='Quantidade', 
                names='Gênero',
                title="Distribuição Percentual do Corpus",
                color_discrete_sequence=self.colors,
                hole=0.4
            )
            st.plotly_chart(fig_pie, width='stretch')

        # 4. Detalhes Técnicos
        with st.expander("Ver base de dados desta análise"):
            st.dataframe(contagem_jornal, width='stretch')

