import streamlit as st
import plotly.express as px

import streamlit as st
import plotly.express as px

class AnaliseAutoria:
    def __init__(self, df, colors):
        """
        Inicia a classe com o dataframe e a paleta de cores padrão.
        """
        self.df = df
        self.colors = colors
        self.col_autor = 'autoria'
        

    def renderizar(self):
        st.header("✍️ Distribuição e Tipologia de Autoria")
        
        if self.col_autor not in self.df.columns:
            st.error(f"Coluna '{self.col_autor}' não encontrada.")
            return

        # 1. TRATAMENTO DE DADOS: REMOVER NULOS E VAZIOS
        # Criamos uma cópia e filtramos para manter apenas quem tem valor preenchido
        df_validos = self.df.copy()
        df_validos = df_validos[
            df_validos[self.col_autor].notna() & 
            (df_validos[self.col_autor].astype(str).str.strip() != '')
        ]

        if df_validos.empty:
            st.warning("Não há dados de autoria preenchidos para os filtros selecionados.")
            return

        # 2. Indicadores Globais (KPIs baseados apenas nos válidos)
        contagem_geral = df_validos[self.col_autor].value_counts()
        total_validos = len(df_validos)
        
        st.caption(f"Análise baseada em {total_validos} publicações com autoria identificada.")
        
        cols = st.columns(min(len(contagem_geral), 4))
        for i, (cat, freq) in enumerate(contagem_geral.items()):
            if i < 4:
                with cols[i]:
                    perc = (freq / total_validos) * 100
                    st.metric(cat, f"{freq} n", f"{perc:.1f}%")

        st.divider()

        # 3. Visualizações
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("📊 Distribuição Global (Autoria Identificada)")
            fig_pie = px.pie(
                df_validos, names=self.col_autor, 
                color_discrete_sequence=self.colors,
                hole=0.4
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, width='stretch')

        with c2:
            st.subheader("📰 Autoria por Jornal (%)")
            # Percentagem relativa apenas dentro do universo de autoria identificada de cada jornal
            df_prop = df_validos.groupby(['jornal', self.col_autor]).size().reset_index(name='n')
            df_prop['percentagem'] = df_prop.groupby('jornal')['n'].transform(lambda x: (x / x.sum() * 100).round(1))

            fig_bar = px.bar(
                df_prop, x='jornal', y='percentagem', color=self.col_autor,
                text=df_prop['percentagem'].apply(lambda x: f'{x}%'),
                color_discrete_sequence=self.colors,
                barmode='group'
            )
            fig_bar.update_layout(yaxis_title="Percentagem (%)", xaxis_title=None)
            st.plotly_chart(fig_bar, width='stretch')



