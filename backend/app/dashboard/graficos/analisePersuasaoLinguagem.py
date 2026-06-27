import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import streamlit as st
import pandas as pd
from scipy.stats import chi2_contingency
import dicionario

class AnalisePersuasaoLinguagem:
    def __init__(self, df, colors):
        self.df = df
        self.colors = colors

    def renderizar(self):
        st.header("🎯 Cruzamento: Linguagem vs. Persuasão")
        
        # 1. Configuração de colunas e limpeza
        col_persuasao = 'persuasao'
        col_linguagem = 'linguagem'
        
        if col_persuasao not in self.df.columns or col_linguagem not in self.df.columns:
            st.error("Colunas 'persuasao' ou 'linguagem' não encontradas.")
            return

        df_cruz = self.df.dropna(subset=[col_persuasao, col_linguagem]).copy()
        
        # Aplicar mapeamento do dicionário
        df_cruz[col_persuasao] = df_cruz[col_persuasao].map(lambda x: dicionario.MAPA.get(x, x))
        df_cruz[col_linguagem] = df_cruz[col_linguagem].map(lambda x: dicionario.MAPA.get(x, x))

        # --- 2. TABELA DE CONTINGÊNCIA (FREQUÊNCIA ABSOLUTA E %) ---
        st.subheader("📊 Matriz de Articulação Teórico-Metodológica")
        
        tabela_abs = pd.crosstab(df_cruz[col_linguagem], df_cruz[col_persuasao], 
                                 margins=True, margins_name="Total")
        
        tabela_pct = pd.crosstab(df_cruz[col_linguagem], df_cruz[col_persuasao], 
                                 normalize='index') * 100

        c1, c2 = st.columns([1, 1.5])
        
        #with c1:
        st.markdown("**Frequências Absolutas (n)**")
        st.dataframe(tabela_abs, width='stretch')
            
        #with c2:
        st.divider()
        st.markdown("**Distribuição Percentual (por Linguagem)**")
        fig_matrix = px.bar(tabela_pct.drop(columns="Total", errors='ignore'), 
                            orientation='h',
                            title="Proporção de Persuasão por Tipo de Linguagem",
                            color_discrete_map={
                                'Comprometido': self.colors[3], 
                                'Não-comprometido': self.colors[0]
                            })
        fig_matrix.update_layout(xaxis_title="Percentual (%)", yaxis_title="Linguagem")
        st.plotly_chart(fig_matrix, width='stretch')

        # --- 3. INDICADORES ANALÍTICOS (Heatmap de Associação) ---
        st.subheader("🔍 Densidade de Cruzamento")
        
        # Criando um gráfico de calor para visualizar onde a concentração é maior
        z_values = pd.crosstab(df_cruz[col_linguagem], df_cruz[col_persuasao]).values
        x_labels = pd.crosstab(df_cruz[col_linguagem], df_cruz[col_persuasao]).columns
        y_labels = pd.crosstab(df_cruz[col_linguagem], df_cruz[col_persuasao]).index

        fig_heat = ff.create_annotated_heatmap(
            z=z_values, 
            x=list(x_labels), 
            y=list(y_labels), 
            colorscale='Blues',
            annotation_text=z_values.astype(str)
        )
        st.plotly_chart(fig_heat, width='stretch')

        # --- 4. TESTE DE ASSOCIAÇÃO ---
        st.subheader("🧪 Significância da Relação")
        chi2, p, dof, expected = chi2_contingency(pd.crosstab(df_cruz[col_linguagem], df_cruz[col_persuasao]))
        
        col_res1, col_res2 = st.columns(2)
        col_res1.metric("P-Value", f"{p:.4e}")
        
        if p < 0.05:
            st.success("✅ Existe uma associação estatisticamente significativa entre a linguagem utilizada e o grau de persuasão do título.")
        else:
            st.info("ℹ️ Não foi detectada associação significativa. A linguagem e a persuasão operam de forma independente neste corpus.")

        with st.expander("Ver Proporções Detalhadas"):
            st.write("**Proporção de comprometimento por linguagem:**")
            for ling in tabela_pct.index:
                comp_val = tabela_pct.loc[ling, 'Comprometido'] if 'Comprometido' in tabela_pct.columns else 0
                st.write(f"- {ling}: {comp_val:.2f}% dos títulos são comprometidos.")