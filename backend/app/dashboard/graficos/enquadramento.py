import plotly.express as px
import streamlit as st
import pandas as pd
from scipy.stats import chi2_contingency
import dicionario

class AnaliseEnquadramento:
    def __init__(self, df, colors):
        self.df = df
        self.colors = colors

    def renderizar(self):
        st.header("🖼️ Enquadramento Jornalístico Dominante")

        col_alvo = 'enqDominante' # Ajuste para o nome da coluna no seu banco
        if col_alvo not in self.df.columns:
            st.error(f"Coluna '{col_alvo}' não encontrada.")
            return

        # 1. Limpeza e Mapeamento
        df_frame = self.df.copy()
        df_frame = df_frame[df_frame[col_alvo].notna() & (df_frame[col_alvo].astype(str).str.strip() != '')]
        df_frame[col_alvo] = df_frame[col_alvo].map(lambda x: dicionario.MAPA.get(x, x))

        # --- 1. INDICADORES DE PREDOMINÂNCIA E CONCENTRAÇÃO (KPIs) ---
        total_n = len(df_frame)
        contagem = df_frame[col_alvo].value_counts()
        
        # Cálculo do Índice de Concentração (Top 2 frames)
        top_2_sum = contagem.iloc[:2].sum() if len(contagem) >= 2 else contagem.sum()
        indice_concentracao = (top_2_sum / total_n) * 100 if total_n > 0 else 0
        
        # Diversidade (Número efetivo de frames usados)
        diversidade = df_frame[col_alvo].nunique()

        c1, c2, c3 = st.columns(3)
        c1.metric("Frame Dominante", contagem.idxmax() if not contagem.empty else "N/A")
        c2.metric("Concentração (Top 2)", f"{indice_concentracao:.1f}%")
        c3.metric("Diversidade de Frames", f"{diversidade} / 6")

        st.divider()

        # --- 2. SISTEMA DE ABAS ---
        tab_dist, tab_comparativo, tab_temporal = st.tabs([
            "📊 Distribuição Geral", 
            "📰 Comparativo por Jornal", 
            "⏳ Variação Temporal"
        ])

        with tab_dist:
            col_a, col_b = st.columns([1.5, 1])
            with col_a:
                df_bar = contagem.reset_index()
                df_bar.columns = [col_alvo, 'n']
                fig_bar = px.bar(df_bar, x='n', y=col_alvo, orientation='h', text='n',
                                 title="Frequência Absoluta de Enquadramentos",
                                 color=col_alvo, color_discrete_sequence=self.colors)
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar, width='stretch')
            
            with col_b:
                fig_pie = px.pie(df_frame, names=col_alvo, hole=0.4,
                                 title="Distribuição Percentual (%)",
                                 color_discrete_sequence=self.colors)
                st.plotly_chart(fig_pie, width='stretch')

        with tab_comparativo:
            st.markdown("**Predominância de Frames por Veículo**")
            df_comp = df_frame.groupby(['jornal', col_alvo]).size().reset_index(name='n')
            # Percentual relativo ao jornal
            df_comp['pct'] = df_comp.groupby('jornal')['n'].transform(lambda x: (x / x.sum()) * 100)
            
            fig_comp = px.bar(df_comp, x='jornal', y='pct', color=col_alvo, 
                             text=df_comp['pct'].apply(lambda x: f'{x:.1f}%'),
                             title="Distribuição Percentual por Jornal",
                             color_discrete_sequence=self.colors)
            st.plotly_chart(fig_comp, width='stretch')

        with tab_temporal:
            st.markdown("**Evolução dos Enquadramentos ao Longo do Tempo**")
            df_evol = df_frame.groupby(['Ano_Int', col_alvo]).size().reset_index(name='n')
            # Normalização anual
            df_evol['pct_anual'] = df_evol.groupby('Ano_Int')['n'].transform(lambda x: (x / x.sum()) * 100)
            
            fig_evol = px.line(df_evol, x='Ano_Int', y='pct_anual', color=col_alvo, markers=True,
                              title="Variação Temporal (%) dos Enquadramentos",
                              labels={'pct_anual': '% do total anual', 'Ano_Int': 'Ano'})
            st.plotly_chart(fig_evol, width='stretch')

        # --- 3. TESTES ESTATÍSTICOS ---
        st.divider()
        st.subheader("🧪 Análise de Significância")
        
        contingencia = pd.crosstab(df_frame['jornal'], df_frame[col_alvo])
        if not contingencia.empty:
            chi2, p, dof, expected = chi2_contingency(contingencia)
            
            st.write(fr"**Teste Qui-Quadrado ($\chi^2$):**")
            res_col1, res_col2 = st.columns(2)
            res_col1.write(f"Estatística: {chi2:.4f}")
            res_col2.write(f"P-Value: {p:.4e}")
            
            if p < 0.05:
                st.success("O enquadramento dominante está significativamente associado ao jornal.")
            else:
                st.info("Não há evidência de associação significativa entre o jornal e o enquadramento.")

        with st.expander("Ver Tabela de Frequências Detalhada"):
            st.dataframe(contingencia, width='stretch')