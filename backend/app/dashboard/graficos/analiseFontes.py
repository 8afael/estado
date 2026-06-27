import plotly.express as px
import streamlit as st
import pandas as pd
import sqlite3
import dicionario
import bd
from graficos import cores

class AnaliseFontes:
    def __init__(self, df_selecionado, colors):
        self.df = df_selecionado
        self.colors = colors
        self.db_path = bd.BD 

    @st.cache_data
    def get_fontes_data(_self, ids_noticias):
        """Busca a frequência das fontes na relação N:N"""
        if not ids_noticias:
            return pd.DataFrame()
        
        conn = sqlite3.connect(_self.db_path)
        # Query baseada na estrutura N:N (tabela fontes e jornal_fontes)
        query = f"""
            SELECT f.descricao as fonte_bruta, COUNT(jf.fonte_id) as total
            FROM fontes f
            JOIN jornal_fontes jf ON f.id = jf.fonte_id
            WHERE jf.jornal_id IN ({','.join(map(str, ids_noticias))})
            GROUP BY f.descricao
            ORDER BY total DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def renderizar(self):
        st.header("🗣️ Análise de Fontes (Quem fala na notícia?)")

        ids_vivos = self.df['id'].tolist()
        df_fontes = self.get_fontes_data(ids_vivos)

        if df_fontes.empty:
            st.warning("Nenhuma fonte encontrada para os critérios selecionados.")
            return

        # 1. Aplicação do Dicionário para tradução/limpeza
        df_fontes['Fonte'] = df_fontes['fonte_bruta'].apply(lambda x: dicionario.MAPA.get(x, x))

        # Re-agrupar caso o dicionário tenha unido categorias (ex: 'Cientista 1' e 'Cientista 2' virarem 'Cientistas')
        df_fontes = df_fontes.groupby('Fonte')['total'].sum().reset_index().sort_values('total', ascending=False)

        # 2. Layout de Visualização
        col_graf, col_info = st.columns([2, 1])


        fig_fontes = px.bar(
            df_fontes.head(15), # Top 15 fontes para não poluir
            x='total',
            y='Fonte',
            orientation='h',
            title="Top 15 Fontes mais Frequentes",
            color='total',
            color_discrete_map=cores.CORES_JORNAIS,
            labels={'total': 'Frequência (n)', 'Fonte': 'Tipo de Fonte'}
        )
        fig_fontes.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_fontes, width='stretch')

        
        st.subheader("Resumo Quantitativo")
        total_citacoes = df_fontes['total'].sum()
        st.metric("Total de Citações", total_citacoes)
        
        # Cálculo de porcentagem
        df_fontes['%'] = (df_fontes['total'] / total_citacoes * 100).round(1)
        st.dataframe(
            df_fontes[['Fonte', 'total', '%']].head(10),
            hide_index=True,
            width='stretch'
        )

        # 3. Gráfico de Treemap (excelente para hierarquia de fontes)
        st.subheader("Visão Geral do Ecossistema de Fontes")
        fig_tree = px.treemap(
            df_fontes, 
            path=['Fonte'], 
            values='total',
            color='total',
            color_continuous_scale='RdBu_r'
        )
        st.plotly_chart(fig_tree, width='stretch')