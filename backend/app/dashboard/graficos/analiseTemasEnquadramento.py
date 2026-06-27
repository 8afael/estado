import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st
import pandas as pd
import sqlite3
import dicionario, bd

class AnaliseCruzamentoTemasEnquadramento:
    def __init__(self, df_selecionado, colors):
        self.df = df_selecionado
        self.colors = colors
        self.db_path = bd.BD 

    @st.cache_data
    def get_dados_relacionais(_self, ids_noticias, tabela_rel, tabela_dim, fk_col):
        if not ids_noticias:
            return pd.DataFrame()
        
        conn = sqlite3.connect(_self.db_path)
        query = f"""
            SELECT rel.jornal_id, dim.descricao as valor
            FROM {tabela_dim} dim
            JOIN {tabela_rel} rel ON dim.id = rel.{fk_col}
            WHERE rel.jornal_id IN ({','.join(map(str, ids_noticias))})
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def renderizar(self):
        st.header("🔗 Articulação: Temas × Enquadramentos")

        ids_vivos = self.df['id'].tolist()

        # 1. Busca de dados
        df_temas_raw = self.get_dados_relacionais(ids_vivos, 'jornal_temas', 'temas', 'tema_id')
        df_enq_raw = self.get_dados_relacionais(ids_vivos, 'jornal_enquadramentos', 'enquadramentos', 'enquadramento_id')

        if df_temas_raw.empty or df_enq_raw.empty:
            st.warning("Dados insuficientes para realizar o cruzamento.")
            return

        # 2. APLICAÇÃO RÍGIDA DO DICIONÁRIO
        # Criamos colunas 'tema' e 'enquadramento' já traduzidas
        df_temas_raw['tema'] = df_temas_raw['valor'].apply(lambda x: dicionario.MAPA.get(x, x))
        df_enq_raw['enquadramento'] = df_enq_raw['valor'].apply(lambda x: dicionario.MAPA.get(x, x))

        # 3. CRUZAMENTO
        df_cruzado = pd.merge(
            df_temas_raw[['jornal_id', 'tema']], 
            df_enq_raw[['jornal_id', 'enquadramento']], 
            on='jornal_id'
        )

        # 4. MATRIZES (usando as colunas já traduzidas)
        ct_abs = pd.crosstab(df_cruzado['tema'], df_cruzado['enquadramento'])
        
        # Garantir que não haja divisão por zero e normalizar
        ct_pct = ct_abs.div(ct_abs.sum(axis=1), axis=0).fillna(0) * 100

        tab_barras, tab_heatmap = st.tabs(["📊 Barras Empilhadas", "🔥 Heatmap de Associação"])

        with tab_barras:
            # Transformar para formato longo para o Plotly Express
            df_plot = ct_pct.reset_index().melt(id_vars='tema', var_name='Enquadramento', value_name='%')
            
            fig_bar = px.bar(
                df_plot, x='%', y='tema', color='Enquadramento',
                orientation='h',
                title="Perfil Interpretativo (Nomes do Dicionário)",
                color_discrete_sequence=self.colors,
                labels={'tema': 'Tema Ambiental', 'Enquadramento': 'Enquadramento Dominante'}
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, barmode='stack')
            st.plotly_chart(fig_bar, width='stretch')

        with tab_heatmap:
            # Para o Heatmap, as labels de X e Y devem vir direto da matriz traduzida
            z_values = ct_pct.round(1).values
            x_labels = [str(col) for col in ct_pct.columns]
            y_labels = [str(idx) for idx in ct_pct.index]

            fig_heat = ff.create_annotated_heatmap(
                z=z_values,
                x=x_labels,
                y=y_labels,
                colorscale='YlGnBu',
                showscale=True
            )
            # Ajuste de layout para garantir que nomes longos do dicionário apareçam
            fig_heat.update_layout(
                margin=dict(l=200, r=50, t=50, b=50),
                xaxis_title="Enquadramentos",
                yaxis_title="Temas"
            )
            st.plotly_chart(fig_heat, width='stretch')

        with st.expander("Ver Frequências Absolutas (n)"):
            st.dataframe(ct_abs, width='stretch')

