import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from scipy.stats import chi2_contingency
import dicionario

class AnalisePersuasao:
    def __init__(self, df, colors):
        self.df = df
        self.colors = colors

    def renderizar(self):
        st.header("📊 Classificação do Título segundo a Persuasão (Mesquita, 2022)")
        
        # Verificação se a coluna existe
        col_alvo = 'persuasao' # Altere para o nome exato da sua coluna
        if col_alvo not in self.df.columns:
            st.error(f"Coluna '{col_alvo}' não encontrada no banco de dados.")
            return
        
        df_validos = self.df.copy()
        df_validos = df_validos[
            df_validos[col_alvo].notna() & 
            (df_validos[col_alvo].astype(str).str.strip() != '')
        ]

        df_validos[col_alvo] = df_validos[col_alvo].map(lambda x: dicionario.MAPA.get(x, x))        


        # --- 1. INDICADORES PRINCIPAIS (KPIs) ---
        total = len(df_validos)
        contagem = df_validos[col_alvo].value_counts()
        n_comp = contagem.get('Comprometido', 0)
        n_ncomp = contagem.get('Não-comprometido', 0)
        razao = n_comp / n_ncomp if n_ncomp > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Títulos", total)
        col2.metric("Razão Comprometido/Não", f"{razao:.2f}")
        col3.metric("Categoria Dominante", contagem.idxmax() if not contagem.empty else "N/A")

        # --- 2. DISTRIBUIÇÃO GERAL E POR JORNAL ---
        col_a, col_b = st.columns(2)

        with col_a:
            fig_pizza = px.pie(df_validos, names=col_alvo, title="Distribuição Total do Corpus",
                             color_discrete_sequence=[self.colors[2], self.colors[3]])
            st.plotly_chart(fig_pizza, width='stretch')

        with col_b:
            # Distribuição Cruzada: Persuasão x Jornal
            df_jornal = df_validos.groupby(['jornal', col_alvo]).size().reset_index(name='frequencia')
            fig_bar = px.bar(df_jornal, x='jornal', y='frequencia', color=col_alvo,
                           title="Persuasão por Jornal", barmode='group',
                           color_discrete_map={'Comprometido': self.colors[3], 'Não-comprometido': self.colors[0]})
            st.plotly_chart(fig_bar, width='stretch')

        # --- 3. EVOLUÇÃO TEMPORAL ---
        st.subheader("📈 Evolução Temporal (Variação Percentual)")
        df_tempo = df_validos.groupby(['Ano_Int', col_alvo]).size().unstack(fill_value=0)
        df_tempo_pct = df_tempo.div(df_tempo.sum(axis=1), axis=0) * 100
        
        fig_evol = px.line(df_tempo_pct, title="Percentual de Títulos ao Longo dos Anos",
                          labels={'value': '% do Total Anual', 'Ano_Int': 'Ano'})
        st.plotly_chart(fig_evol, width='stretch')

        # --- 4. TESTES ESTATÍSTICOS ---
        st.divider()
        st.subheader("🧪 Testes Estatísticos (Associação)")
        
        # Tabela de Contingência para Qui-Quadrado
        contingencia = pd.crosstab(df_validos['jornal'], df_validos[col_alvo])
        
        if not contingencia.empty:
            chi2, p, dof, expected = chi2_contingency(contingencia)
            
            exp = st.expander("Ver Resultados do Teste Qui-Quadrado (Jornal × Persuasão)")
            exp.write(f"**Estatística Chi2:** {chi2:.4f}")
            exp.write(f"**P-Value:** {p:.4e}")
            if p < 0.05:
                exp.success("Resultado Significativo: Existe associação entre o jornal e o tipo de persuasão.")
            else:
                exp.info("Não há evidência estatística de associação significativa entre o jornal e a persuasão.")
            exp.write("Frequências Esperadas:")
            exp.write(expected)