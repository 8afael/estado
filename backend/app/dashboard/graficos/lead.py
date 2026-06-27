import plotly.express as px
import streamlit as st
import pandas as pd
from scipy.stats import chi2_contingency
import dicionario

class AnaliseLeadQuant:
    def __init__(self, df, colors):
        self.df = df
        self.colors = colors

    def renderizar(self):
        st.header("📊 Análise Quantitativa dos Leads")

        col_alvo = 'lead' 
        if col_alvo not in self.df.columns:
            st.error(f"Coluna '{col_alvo}' não encontrada.")
            return
        
        # Filtro de dados válidos
        df_validos = self.df.copy()
        df_validos = df_validos[
            df_validos[col_alvo].notna() & 
            (df_validos[col_alvo].astype(str).str.strip() != '')
        ]

        # 1. Limpeza e Mapeamento
        df_lead = df_validos.copy()
        df_lead[col_alvo] = df_lead[col_alvo].map(lambda x: dicionario.MAPA.get(x, x))

        # --- 1. INDICADORES PRINCIPAIS (KPIs) ---
        total_leads = len(df_lead)
        contagem = df_lead[col_alvo].value_counts()
        categoria_dominante = contagem.idxmax() if not contagem.empty else "N/A"
        pct_dominante = (contagem.max() / total_leads) * 100 if total_leads > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Leads (n)", total_leads)
        c2.metric("Categoria Dominante", categoria_dominante)
        c3.metric("Representatividade (%)", f"{pct_dominante:.1f}%")

        st.divider()

        # --- 2. SISTEMA DE ABAS ---
        tab_total, tab_jornal, tab_evolucao = st.tabs([
            "📈 Frequência Total", 
            "📰 Por Jornal", 
            "⏳ Evolução Histórica"
        ])

        with tab_total:
            st.markdown("**Frequência Absoluta por Tipo de Lead (Corpus Total)**")
            df_total = contagem.reset_index()
            df_total.columns = [col_alvo, 'n']
            
            fig_total = px.bar(
                df_total,
                x=col_alvo,
                y='n',
                text='n',
                color=col_alvo,
                title="Distribuição Geral de Tipos de Lead",
                color_discrete_sequence=self.colors
            )
            fig_total.update_traces(textposition='outside')
            fig_total.update_layout(xaxis_title="Tipo de Lead", yaxis_title="Frequência (n)")
            st.plotly_chart(fig_total, width='stretch')

            # Gráfico de Pizza movido para dentro da aba total para complementar
            st.markdown("---")
            fig_pizza = px.pie(
                df_lead, 
                names=col_alvo, 
                hole=0.4,
                color_discrete_sequence=self.colors,
                title="Representação Percentual no Corpus"
            )
            fig_pizza.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pizza, width='stretch')

        with tab_jornal:
            st.markdown("**Frequência de Leads por Jornal**")
            df_jornal = df_lead.groupby(['jornal', col_alvo]).size().reset_index(name='n')
            
            fig_jornal = px.bar(
                df_jornal, 
                x='jornal', 
                y='n', 
                color=col_alvo, 
                barmode='group',
                text='n',
                title="Distribuição Absoluta por Jornal",
                color_discrete_sequence=self.colors
            )
            fig_jornal.update_traces(textposition='outside')
            st.plotly_chart(fig_jornal, width='stretch')

        with tab_evolucao:
            st.markdown("**Evolução das Categorias ao Longo do Tempo**")
            df_tempo = df_lead.groupby(['Ano_Int', col_alvo]).size().reset_index(name='frequencia')
            
            fig_tempo = px.line(
                df_tempo, 
                x='Ano_Int', 
                y='frequencia', 
                color=col_alvo,
                markers=True,
                title="Frequência Absoluta ao Longo do Tempo",
                labels={'Ano_Int': 'Ano', 'frequencia': 'Número de Notícias'}
            )
            st.plotly_chart(fig_tempo, width='stretch')

        # --- 3. TESTE ESTATÍSTICO ---
        st.divider()
        st.subheader("🧪 Teste de Independência (Qui-Quadrado)")
        contingencia = pd.crosstab(df_lead['jornal'], df_lead[col_alvo])
        
        if not contingencia.empty:
            chi2, p, dof, expected = chi2_contingency(contingencia)
            
            col_res1, col_res2 = st.columns([1, 2])
            with col_res1:
                st.write(fr"**$\chi^2$:** {chi2:.2f}")
                st.write(f"**p-value:** {p:.4e}")
            
            with col_res2:
                if p < 0.05:
                    st.success("Existe associação significativa entre a escolha do lead e o jornal.")
                else:
                    st.info("A distribuição dos leads é estatisticamente similar entre os jornais.")

        with st.expander("Ver Tabela de Frequências (n)"):
            st.table(contingencia)


