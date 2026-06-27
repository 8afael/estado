import plotly.express as px
import streamlit as st
import pandas as pd
from scipy.stats import chi2_contingency
import dicionario

class AnalisePapelJornalistico:
    def __init__(self, df, colors):
        self.df = df
        self.colors = colors

    def renderizar(self):
        st.header("🎭 Papel Jornalístico Predominante (1973-2023)")

        col_alvo = 'papJornalistico' # Ajuste para o nome exato no seu BD
        if col_alvo not in self.df.columns:
            st.error(f"Coluna '{col_alvo}' não encontrada.")
            return

        # 1. Limpeza e Mapeamento
        df_papel = self.df.copy()
        df_papel = df_papel[df_papel[col_alvo].notna() & (df_papel[col_alvo].astype(str).str.strip() != '')]
        df_papel[col_alvo] = df_papel[col_alvo].map(lambda x: dicionario.MAPA.get(x, x))

        # --- 1. INDICADORES QUANTITATIVOS PRINCIPAIS (KPIs) ---
        total_n = len(df_papel)
        contagem = df_papel[col_alvo].value_counts()
        
        # Papel Dominante
        dominante = contagem.idxmax() if not contagem.empty else "N/A"
        pct_dominante = (contagem.max() / total_n) * 100 if total_n > 0 else 0
        
        # Razão Empenhado / Neutro (Calculada sobre os nomes mapeados)
        n_empenhado = contagem.get('Empenhado/advocacy', 0)
        n_neutro = contagem.get('Disseminador/neutro', 0)
        razao_adv = n_empenhado / n_neutro if n_neutro > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Registros (n)", total_n)
        c2.metric("Papel Dominante", f"{dominante} ({pct_dominante:.1f}%)")
        c3.metric("Razão Empenhado/Neutro", f"{razao_adv:.2f}")

        st.divider()

        # --- 2. SISTEMA DE ABAS ---
        tab_total, tab_jornal, tab_evolucao = st.tabs([
            "📈 Frequência Total", 
            "📰 Por Jornal", 
            "⏳ Evolução Histórica"
        ])

        with tab_total:
            col_a, col_b = st.columns([1.5, 1])
            with col_a:
                df_total = contagem.reset_index()
                df_total.columns = [col_alvo, 'n']
                fig_total = px.bar(
                    df_total, x=col_alvo, y='n', text='n',
                    title="Distribuição Absoluta do Corpus",
                    color=col_alvo, color_discrete_sequence=self.colors
                )
                fig_total.update_traces(textposition='outside')
                st.plotly_chart(fig_total, width='stretch')
            
            with col_b:
                fig_pizza = px.pie(
                    df_papel, names=col_alvo, hole=0.4,
                    title="Percentagem (%) Total",
                    color_discrete_sequence=self.colors
                )
                fig_pizza.update_traces(textinfo='percent+label')
                st.plotly_chart(fig_pizza, width='stretch')

        with tab_jornal:
            st.markdown("**Distribuição por Jornal**")
            df_jornal = df_papel.groupby(['jornal', col_alvo]).size().reset_index(name='n')
            # % dentro de cada jornal
            df_jornal['pct'] = df_jornal.groupby('jornal')['n'].transform(lambda x: (x / x.sum()) * 100)
            
            fig_jornal = px.bar(
                df_jornal, x='jornal', y='n', color=col_alvo, 
                barmode='group', text='n',
                title="Frequência Absoluta por Jornal",
                color_discrete_sequence=self.colors
            )
            fig_jornal.update_traces(textposition='outside')
            st.plotly_chart(fig_jornal, width='stretch')

        with tab_evolucao:
            st.markdown("**Evolução Temporal (1973 - 2023)**")
            df_tempo = df_papel.groupby(['Ano_Int', col_alvo]).size().reset_index(name='n')
            # Normalização para ver a mudança de perfil independente do volume de notícias
            df_tempo['pct_anual'] = df_tempo.groupby('Ano_Int')['n'].transform(lambda x: (x / x.sum()) * 100)
            
            fig_tempo = px.line(
                df_tempo, x='Ano_Int', y='pct_anual', color=col_alvo,
                markers=True, title="Variação do Papel Jornalístico (%) por Ano",
                labels={'pct_anual': '% do total anual', 'Ano_Int': 'Ano'}
            )
            st.plotly_chart(fig_tempo, width='stretch')

        # --- 3. TESTE ESTATÍSTICO ---
        st.divider()
        st.subheader("🧪 Teste de Independência (Qui-Quadrado)")
        
        contingencia = pd.crosstab(df_papel['jornal'], df_papel[col_alvo])
        if not contingencia.empty:
            chi2, p, dof, expected = chi2_contingency(contingencia)
            
            col_res1, col_res2 = st.columns([1, 2])
            with col_res1:
                st.write(fr"**$\chi^2$:** {chi2:.4f}")
                st.write(f"**p-value:** {p:.4e}")
            
            with col_res2:
                if p < 0.05:
                    st.success("Há evidência de que o papel jornalístico varia significativamente entre os jornais.")
                else:
                    st.info("Não há evidência de associação significativa entre o jornal e o papel desempenhado.")

        with st.expander("Ver Matriz de Frequências (n)"):
            st.dataframe(contingencia, width='stretch')