import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import chi2_contingency
import dicionario

class AnaliseLinguagem:
    def __init__(self, df, colors):
        self.df = df
        self.colors = colors
        self.col_ling = 'linguagem' # Nome da coluna no seu banco

    def renderizar(self):
        st.header("🔡 Classificação da Linguagem dos Títulos (Mesquita, 2022)")
        
        if self.col_ling not in self.df.columns:
            st.error(f"Coluna '{self.col_ling}' não encontrada.")
            return

        # Limpeza e filtragem
        df_ling = self.df.copy()
        df_ling = df_ling[df_ling[self.col_ling].notna() & (df_ling[self.col_ling] != '')]
        df_ling[self.col_ling] = df_ling[self.col_ling].map(lambda x: dicionario.MAPA.get(x, x))

        # --- 1. INDICADORES GLOBAIS E ÍNDICE DE EXPRESSIVIDADE ---
        total = len(df_ling)
        # Definindo grupos para o Índice de Expressividade
        inf_cats = ['Informativo indicativo', 'Informativo explicativo']
        exp_cats = ['Expressivo apelativo', 'Expressivo formal ou lúdico', 'Expressivo interrogativo']
        
        n_inf = df_ling[self.col_ling].isin(inf_cats).sum()
        n_exp = df_ling[self.col_ling].isin(exp_cats).sum()
        indice_exp = (n_exp / total) * 100

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total de Títulos Analisados", f"{total} n")
        with c2:
            st.metric("Categoria Dominante", df_ling[self.col_ling].mode()[0])
        with c3:
            st.metric("Índice de Expressividade", f"{indice_exp:.1f}%", help="Proporção de títulos expressivos vs informativos")

        st.divider()

        # --- 2. DISTRIBUIÇÃO E VARIAÇÃO POR JORNAL ---
        st.subheader("📰 Linguagem por Jornal")
        df_jr = df_ling.groupby(['jornal', self.col_ling]).size().reset_index(name='n')
        df_jr['%'] = df_jr.groupby('jornal')['n'].transform(lambda x: (x / x.sum() * 100).round(1))

        fig_jr = px.bar(
            df_jr, x='jornal', y='%', color=self.col_ling,
            text=df_jr['%'].apply(lambda x: f'{x}%'),
            barmode='group', color_discrete_sequence=self.colors
        )
        st.plotly_chart(fig_jr, width='stretch')

        # --- 3. TESTE ESTATÍSTICO: QUI-QUADRADO (χ²) ---
        st.subheader("🧪 Teste de Associação (Qui-quadrado)")
        
        # Tabela de Contingência
        contingency_table = pd.crosstab(df_ling['jornal'], df_ling[self.col_ling])
        chi2, p, dof, expected = chi2_contingency(contingency_table)

        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.write("**Associação Linguagem × Jornal**")
            st.write(f"- Valor $\chi^2$: `{chi2:.2f}`")
            st.write(f"- $p$-value: `{p:.4f}`")
            if p < 0.05:
                st.success("✅ Existe uma associação significativa entre o tipo de jornal e a linguagem utilizada.")
            else:
                st.info("ℹ️ Não há evidência de associação significativa entre o jornal e a linguagem.")

        # --- 4. VARIAÇÃO TEMPORAL POR DÉCADA ---
        st.divider()
        st.subheader("⏳ Variação Temporal por Década")
        df_dec = df_ling.groupby(['Década', self.col_ling]).size().reset_index(name='n')
        df_dec['%'] = df_dec.groupby('Década')['n'].transform(lambda x: (x / x.sum() * 100).round(1))

        fig_temp = px.area(
            df_dec, x='Década', y='%', color=self.col_ling,
            color_discrete_sequence=self.colors,
            title="Evolução da Composição da Linguagem (1973-2023)"
        )
        st.plotly_chart(fig_temp, width='stretch')