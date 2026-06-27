import streamlit as st
import plotly.express as px

class AnaliseAbrangencia:
    def __init__(self, df, colors):
        self.df = df
        self.colors = colors
        self.col_geo = 'abrangencia' # Nome da coluna no seu DB

    def renderizar(self):
        st.header("🌍 Abrangência Geográfica da Informação")
        st.markdown("""
        Esta análise mapeia o foco espacial das notícias, permitindo identificar se a cobertura ambiental 
        é predominantemente local/regional, focada em políticas nacionais ou em dinâmicas globais.
        """)

        if self.col_geo not in self.df.columns:
            st.error(f"Coluna '{self.col_geo}' não encontrada.")
            return

        # Limpeza de dados (removendo vazios para esta análise específica)
        df_geo = self.df.copy()
        df_geo = df_geo[df_geo[self.col_geo].notna() & (df_geo[self.col_geo] != '')]

        # --- 1. EVOLUÇÃO TEMPORAL (1973-2023) ---
        st.subheader("📈 Evolução Histórica da Abrangência")
        
        # Agrupamento por década para suavizar a linha e ver tendências de longo prazo
        df_temp = df_geo.groupby(['Década', self.col_geo]).size().reset_index(name='n')
        
        fig_temp = px.line(
            df_temp, x='Década', y='n', color=self.col_geo,
            markers=True,
            color_discrete_sequence=self.colors,
            title="Volume de Notícias por Foco Geográfico ao Longo das Décadas"
        )
        fig_temp.update_layout(xaxis_title="Década", yaxis_title="Número de Publicações")
        st.plotly_chart(fig_temp, width='stretch')

        st.divider()

        # --- 2. DIFERENÇAS ENTRE JORNAIS ---
        st.subheader("📰 Predominância por Jornal")
        
        df_comp = df_geo.groupby(['jornal', self.col_geo]).size().reset_index(name='n')
        df_comp['%'] = df_comp.groupby('jornal')['n'].transform(lambda x: (x / x.sum() * 100).round(1))

        fig_bar = px.bar(
            df_comp, x='jornal', y='%', color=self.col_geo,
            text=df_comp['%'].apply(lambda x: f'{x}%'),
            color_discrete_sequence=self.colors,
            title="Perfil Editorial: Regional vs Nacional vs Internacional"
        )
        fig_bar.update_layout(yaxis_title="Percentagem (%) do Corpus do Jornal", xaxis_title=None)
        st.plotly_chart(fig_bar, width='stretch')

