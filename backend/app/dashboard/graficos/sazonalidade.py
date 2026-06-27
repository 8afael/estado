import streamlit as st
import plotly.express as px
import dicionario
from graficos import cores

class Sazonalidade:
    def __init__(self, df, colors):
        self.df = df
        self.colors = colors
        # Definimos a lista ordenada de meses para garantir que o gráfico não embaralhe a ordem (Jan, Fev...)
        self.lista_meses = list(dicionario.MESES_PT_MAPA.values())

    def renderizar(self):
        st.title("📊 Análise do Corpus: Cobertura Ambiental")
        
        # 1. KPIs Iniciais
        col_kpi, col_jornais = st.columns([1, 3])
        with col_kpi:
            st.subheader("🧐 Evolução")
            total = len(self.df)
            st.metric("Total de Publicações", f"{total}")
            st.metric("Jornais", f"{self.df['jornal'].nunique()}")

        with col_jornais:
            df_jornais = self.df.groupby('jornal').size().reset_index(name='Total')
            fig_jornais = px.bar(df_jornais, x='jornal', y='Total', color='jornal', 
                                 color_discrete_map=cores.CORES_JORNAIS, text_auto=True)
            st.plotly_chart(fig_jornais, width='stretch')

        st.divider()

        # 2. CRUZAMENTOS DINÂMICOS
        st.subheader("📈 Cruzamentos Dinâmicos")
        colunas_cruzamento = dicionario.CRUZAMENTO
        
        c1, c2, c3 = st.columns(3)
        with c1:
            # AJUSTE AQUI: O label é amigável, mas o valor (opções) deve ser o nome real da coluna no DF
            mapa_tempo = {
                "Ano": "Ano_Int",
                "Década": "Década",
                "Mês": "Mes_Nome",
                "Dia": "dataPublicacao" # Ou 'Dia' se formatado como string
            }
            label_x = st.selectbox("Eixo X (Base):", list(mapa_tempo.keys()), index=0)
            coluna_x = mapa_tempo[label_x] # Pega o nome real da coluna (ex: 'Ano_Int')
            
        with c2:
            cor_cruzamento = st.selectbox("Cruzar com (Cores):", [None] + colunas_cruzamento, index=1)
        with c3:
            tipo_grafico = st.radio("Formato:", ["Barras", "Torta"], horizontal=True)

        df_visual = self.df.copy()
        
        if cor_cruzamento and cor_cruzamento in df_visual.columns:
            df_visual[cor_cruzamento] = df_visual[cor_cruzamento].map(lambda x: dicionario.MAPA.get(x, x))

        if tipo_grafico == "Barras":
            fig = px.histogram(
                df_visual, 
                x=coluna_x, # Usando o nome real da coluna
                color=cor_cruzamento, 
                color_discrete_map=cores.CORES_JORNAIS, 
                text_auto=True, 
                barmode='stack'
            )
            fig.update_xaxes(type='category', categoryorder='category ascending')
        else:
            fig = px.pie(df_visual, names=coluna_x, hole=0.3, color_discrete_map=cores.CORES_JORNAIS)
        
        st.plotly_chart(fig, width='stretch')

        # 3. SAZONALIDADE MENSAL
        st.divider()
        st.subheader("🗓️ Sazonalidade Mensal")

        # Agrupamento para os gráficos mensais
        df_mes_jornal = self.df.groupby(['Mes_Nome', 'Mes_Num', 'jornal']).size().reset_index(name='Total')
        df_mes_jornal = df_mes_jornal.sort_values('Mes_Num')

        col_mes1, col_mes2 = st.columns(2)
        
        with col_mes1:
            # AJUSTE: self.colors em vez de self.bootstrap_colors
            fig_vol = px.bar(df_mes_jornal, x='Mes_Nome', y='Total', color='jornal', 
                             text_auto=True, color_discrete_map=cores.CORES_JORNAIS, 
                             title="Volume Acumulado por Mês")
            # AJUSTE: self.lista_meses em vez de self.LISTA_MESES_ORDENADA
            fig_vol.update_layout(xaxis_title=None, xaxis={'categoryorder':'array', 'categoryarray': self.lista_meses})
            st.plotly_chart(fig_vol, width='stretch')
            
        with col_mes2:
            df_mes_perc = df_mes_jornal.copy()
            df_mes_perc['Percentagem'] = df_mes_perc.groupby('jornal')['Total'].transform(lambda x: (x / x.sum()) * 100)
            
            # AJUSTE: self.colors em vez de self.bootstrap_colors
            fig_conc = px.line(df_mes_perc, x='Mes_Nome', y='Percentagem', color='jornal', 
                               markers=True, color_discrete_map=cores.CORES_JORNAIS, 
                               title="Concentração Mensal %")
            # AJUSTE: self.lista_meses
            fig_conc.update_layout(xaxis_title=None, xaxis={'categoryorder':'array', 'categoryarray': self.lista_meses})
            st.plotly_chart(fig_conc, width='stretch')

