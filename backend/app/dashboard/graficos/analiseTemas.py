import plotly.express as px
import streamlit as st
import pandas as pd
import sqlite3
from scipy.stats import chi2_contingency
import dicionario
import bd

class AnaliseTemas:
    def __init__(self, df_selecionado, colors):
        self.df = df_selecionado
        self.colors = colors
        self.db_path = bd.BD 

    @st.cache_data
    def get_temas_data(_self, ids_noticias):
        if not ids_noticias:
            return pd.DataFrame()
        
        conn = sqlite3.connect(_self.db_path)
        query = f"""
            SELECT jt.jornal_id, t.descricao as tema
            FROM temas t
            JOIN jornal_temas jt ON t.id = jt.tema_id
            WHERE jt.jornal_id IN ({','.join(map(str, ids_noticias))})
        """
        df_rel = pd.read_sql(query, conn)
        conn.close()
        return df_rel

    def renderizar(self):
        st.header("🌿 Agenda Temática (1973-2023)")

        # 1. Carregar e Mapear Dados
        ids_vivos = self.df['id'].tolist()
        df_relacao = self.get_temas_data(ids_vivos)
        
        # Aplicar mapeamento do dicionário
        df_relacao['tema'] = df_relacao['tema'].map(lambda x: dicionario.MAPA.get(x, x))

        if df_relacao.empty:
            st.warning("Nenhum tema encontrado para as notícias selecionadas.")
            return

        # Merge para associar os temas aos nomes dos jornais
        df_completo = pd.merge(
            df_relacao, 
            self.df[['id', 'jornal', 'Ano_Int']], 
            left_on='jornal_id', 
            right_on='id'
        )

        # --- 1. INDICADORES (KPIs) ---
        total_noticias = len(self.df)
        contagem_por_noticia = df_relacao.groupby('jornal_id').size()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Notícias", total_noticias)
        c2.metric("Média de Temas/Notícia", f"{contagem_por_noticia.mean():.2f}")
        c3.metric("Diversidade Temática", f"{df_relacao['tema'].nunique()} Temas")

        st.divider()

        # --- 2. ABAS DE ANÁLISE ---
        tab_total, tab_jornal, tab_evolucao = st.tabs([
            "📊 Frequência Geral", 
            "📰 Por Jornal (Predominância)", 
            "⏳ Evolução Histórica"
        ])

        with tab_total:
            freq_abs = df_relacao['tema'].value_counts().reset_index()
            freq_abs.columns = ['Tema', 'n']
            freq_abs['%'] = (freq_abs['n'] / total_noticias) * 100
            
            fig_total = px.bar(freq_abs, x='%', y='Tema', orientation='h',
                               text=freq_abs['n'].apply(lambda x: f'n={x}'),
                               title="Prevalência Temática Global",
                               color='%', color_continuous_scale='Greens')
            fig_total.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_total, width='stretch')

        with tab_jornal:
            st.subheader("🏆 Temas Predominantes por Veículo")
            
            # Cálculo de Predominância
            df_jornal = df_completo.groupby(['jornal', 'tema']).size().reset_index(name='n')
            
            # Identificar o top 1 de cada jornal
            predominantes = df_jornal.sort_values(['jornal', 'n'], ascending=[True, False]).groupby('jornal').head(1)
            
            # Exibir resumo de predominância em colunas ou tabela amigável
            cols = st.columns(len(predominantes))
            for i, row in enumerate(predominantes.itertuples()):
                with cols[i]:
                    st.markdown(f"**{row.jornal}**")
                    st.info(f"🥇 {row.tema}\n\n({row.n} ocorrências)")

            st.write("---")

            # Gráfico Comparativo
            fig_jornal = px.bar(df_jornal, x='tema', y='n', color='jornal', barmode='group',
                               title="Distribuição Temática Comparativa",
                               labels={'n': 'Quantidade de Ocorrências', 'tema': 'Tema'},
                               color_discrete_sequence=self.colors)
            st.plotly_chart(fig_jornal, width='stretch')

        with tab_evolucao:
            df_completo['Decada'] = (df_completo['Ano_Int'] // 10 * 10).astype(str) + "s"
            noticias_por_decada = self.df.groupby((self.df['Ano_Int'] // 10 * 10).astype(str) + "s").size()
            
            df_evol = df_completo.groupby(['Decada', 'tema']).size().reset_index(name='n')
            df_evol['pct'] = df_evol.apply(lambda row: (row['n'] / noticias_por_decada.get(row['Decada'], 1)) * 100, axis=1)

            fig_evol = px.line(df_evol, x='Decada', y='pct', color='tema', markers=True,
                               title="Evolução da Agenda Temática por Década (%)")
            st.plotly_chart(fig_evol, width='stretch')

        # --- 3. TESTE ESTATÍSTICO ---
        st.divider()
        st.subheader("🧪 Teste Qui-Quadrado (Associação Tema × Jornal)")
        
        tema_foco = st.selectbox("Selecione um tema para verificar viés editorial:", 
                                 options=sorted(df_relacao['tema'].unique()))
        
        ids_com_tema = df_relacao[df_relacao['tema'] == tema_foco]['jornal_id'].unique()
        df_teste = self.df.copy()
        df_teste['tem_tema'] = df_teste['id'].isin(ids_com_tema).map({True: 'Sim', False: 'Não'})
        
        contingencia = pd.crosstab(df_teste['jornal'], df_teste['tem_tema'])
        if not contingencia.empty:
            chi2, p, _, _ = chi2_contingency(contingencia)
            st.write(f"**Análise de Significância para: {tema_foco}**")
            st.write(f"Estatística Chi²: {chi2:.4f} | p-value: {p:.4e}")
            
            if p < 0.05:
                st.success(f"✅ O tema '{tema_foco}' possui associação significativa com jornais específicos.")
            else:
                st.info("ℹ️ A distribuição deste tema é homogênea entre os jornais analisados.")

