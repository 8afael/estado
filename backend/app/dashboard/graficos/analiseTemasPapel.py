import plotly.express as px
import streamlit as st
import pandas as pd
import sqlite3
import dicionario, bd

class AnaliseTemasPapel:
    def __init__(self, df_selecionado, colors):
        self.df = df_selecionado
        self.colors = colors
        self.db_path = bd.BD 

    @st.cache_data
    def get_temas_data(_self, ids_noticias):
        """Busca temas na relação N:N (Tabelas temas e jornal_temas)"""
        if not ids_noticias:
            return pd.DataFrame()
        
        conn = sqlite3.connect(_self.db_path)
        # Usando os nomes confirmados no seu esquema anterior
        query = f"""
            SELECT rel.jornal_id, dim.descricao as valor
            FROM temas dim
            JOIN jornal_temas rel ON dim.id = rel.tema_id
            WHERE rel.jornal_id IN ({','.join(map(str, ids_noticias))})
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def renderizar(self):
        st.header("🎭 Articulação: Temas × Papel Jornalístico")

        ids_vivos = self.df['id'].tolist()

        # 1. Coleta de Dados de Temas (N:N)
        df_temas_raw = self.get_temas_data(ids_vivos)
        
        if df_temas_raw.empty:
            st.warning("Nenhum tema encontrado para o cruzamento.")
            return

        # 2. Preparação e Tradução (Dicionário)
        # Traduz os temas vindos do banco
        df_temas_raw['tema'] = df_temas_raw['valor'].apply(lambda x: dicionario.MAPA.get(x, x))
        
        # Prepara os papéis vindos da coluna 'papJornalistico' do DataFrame principal
        df_base = self.df[['id', 'papJornalistico', 'Ano_Int']].copy()
        df_base['papel'] = df_base['papJornalistico'].apply(lambda x: dicionario.MAPA.get(x, x))

        # 3. Cruzamento (Merge)
        # Unimos os temas à base de papéis pelo ID da notícia
        df_cruzado = pd.merge(
            df_temas_raw[['jornal_id', 'tema']], 
            df_base[['id', 'papel', 'Ano_Int']], 
            left_on='jornal_id', 
            right_on='id'
        )

        # --- 4. CÁLCULO DA RAZÃO EMPENHADO / NEUTRO ---
        st.subheader("⚖️ Índice de Advocacy por Tema")
        
        ct_papel = pd.crosstab(df_cruzado['tema'], df_cruzado['papel'])
        
        # Defina aqui os nomes exatos que aparecem no seu dicionario.MAPA para estes papéis
        col_empenhado = 'Empenhado' 
        col_neutro = 'Neutro'

        if col_empenhado in ct_papel.columns and col_neutro in ct_papel.columns:
            # Cálculo da razão com proteção contra divisão por zero
            ct_papel['Razão'] = ct_papel[col_empenhado] / (ct_papel[col_neutro] + 0.1)
            df_razao = ct_papel['Razão'].sort_values(ascending=False).reset_index()
            
            fig_razao = px.bar(df_razao, x='Razão', y='tema', orientation='h',
                               title="Predominância de Mobilização (Empenhado vs Neutro)",
                               color='Razão', color_continuous_scale='YlGn')
            st.plotly_chart(fig_razao, width='stretch')
        else:
            st.info("Para visualizar a Razão de Advocacy, certifique-se de que os termos 'Empenhado' e 'Neutro' existem no seu dicionário.")

        # --- 5. ABAS DE ANÁLISE ---
        tab_dist, tab_evol = st.tabs(["📊 Distribuição por Tema", "⏳ Evolução Temporal"])

        with tab_dist:
            # Matriz percentual (cada tema soma 100%)
            ct_pct = ct_papel.drop(columns=['Razão'], errors='ignore')
            ct_pct = ct_pct.div(ct_pct.sum(axis=1), axis=0) * 100
            
            df_plot = ct_pct.reset_index().melt(id_vars='tema', var_name='Papel', value_name='%')

            fig_bar = px.bar(df_plot, x='%', y='tema', color='Papel',
                             barmode='group', title="Papéis Jornalísticos dentro de cada Tema (%)",
                             color_discrete_sequence=self.colors)
            st.plotly_chart(fig_bar, width='stretch')

        with tab_evol:
            tema_foco = st.selectbox("Selecione um tema para analisar a mudança de postura:", 
                                     options=sorted(df_cruzado['tema'].unique()))
            
            df_filtro = df_cruzado[df_cruzado['tema'] == tema_foco].copy()
            df_filtro['Decada'] = (df_filtro['Ano_Int'] // 10 * 10).astype(str) + "s"
            
            # Evolução proporcional dentro do tema
            evol_df = df_filtro.groupby(['Decada', 'papel']).size().reset_index(name='n')
            total_dec = evol_df.groupby('Decada')['n'].transform('sum')
            evol_df['%'] = (evol_df['n'] / total_dec) * 100

            fig_evol = px.line(evol_df, x='Decada', y='%', color='papel', markers=True,
                               title=f"Evolução do Papel Jornalístico: {tema_foco}")
            st.plotly_chart(fig_evol, width='stretch')