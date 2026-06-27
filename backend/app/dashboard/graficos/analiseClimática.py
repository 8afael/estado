import plotly.express as px
import streamlit as st
import pandas as pd

class AnaliseClimatica:
    def __init__(self, df_selecionado, colors):
        self.df = df_selecionado
        self.colors = colors

    def renderizar(self):
        st.header("🌍 Foco: Alterações Climáticas")

        if 'climaticas' not in self.df.columns:
            st.error("A coluna 'climaticas' não foi encontrada na base de dados.")
            return

        # 1. Preparação dos dados
        df_cli = self.df.copy()
        df_cli['Status'] = df_cli['climaticas'].map({1: 'Sim', 0: 'Não'})
        
        # 2. Métricas de Destaque (KPIs)
        total_noticias = len(df_cli)
        total_sim = df_cli['climaticas'].sum()
        percentual_geral = (total_sim / total_noticias * 100).round(1)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Notícias", total_noticias)
        c2.metric("Notícias sobre Clima", total_sim)
        c3.metric("Média Geral (%)", f"{percentual_geral}%")

        st.divider()

        # 3. Análise por Jornal, Proporção e Evolução
        tab_jornal, tab_proporcao, tab_evolucao = st.tabs([
            "📰 Índice por Jornal", 
            "📊 Proporção no Corpus", 
            "📈 Evolução Temporal"
        ])

        with tab_jornal:
            st.subheader("Percentual de Menção Direta por Jornal")
            
            # Cálculo do índice por jornal
            # Agrupamos por jornal e calculamos a média da coluna 'climaticas' (que é 0 ou 1)
            indice_jornal = df_cli.groupby('jornal')['climaticas'].mean().reset_index()
            indice_jornal['Percentual (%)'] = (indice_jornal['climaticas'] * 100).round(2)
            indice_jornal = indice_jornal.sort_values('Percentual (%)', ascending=False)

            # Gráfico de barras horizontais para comparação
            fig_jor = px.bar(
                indice_jornal,
                x='Percentual (%)',
                y='jornal',
                orientation='h',
                text='Percentual (%)',
                title="Índice de Notícias sobre Alterações Climáticas (%)",
                labels={'jornal': 'Jornal', 'Percentual (%)': 'Índice Percentual (%)'},
                color='Percentual (%)',
                color_continuous_scale='Reds'
            )
            fig_jor.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_jor.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_jor, width='stretch')

            # Resposta direta em texto para clareza
            st.info("💡 **Análise de Predominância:** O jornal com maior foco na temática climática neste recorte é o **{}**, com **{}%** de suas notícias citando o tema.".format(
                indice_jornal.iloc[0]['jornal'], 
                indice_jornal.iloc[0]['Percentual (%)']
            ))

        with tab_proporcao:
            contagem = df_cli['Status'].value_counts().reset_index()
            contagem.columns = ['Foco Climático', 'Total']
            
            fig_pie = px.pie(
                contagem, 
                values='Total', 
                names='Foco Climático',
                hole=0.5,
                title="A pauta é sobre Alterações Climáticas?",
                color='Foco Climático',
                color_discrete_map={'Sim': '#ef553b', 'Não': '#636efa'}
            )
            st.plotly_chart(fig_pie, width='stretch')

        with tab_evolucao:
            df_cli['Decada'] = (df_cli['Ano_Int'] // 10 * 10).astype(str) + "s"
            evol_cli = df_cli.groupby(['Decada', 'Status']).size().unstack(fill_value=0)
            
            if 'Sim' not in evol_cli.columns:
                evol_cli['Sim'] = 0
                
            evol_cli['%_Clima'] = (evol_cli['Sim'] / evol_cli.sum(axis=1) * 100).round(2)
            evol_cli = evol_cli.reset_index()

            fig_evol = px.line(
                evol_cli, 
                x='Decada', 
                y='%_Clima',
                markers=True,
                title="Crescimento da Temática Climática por Década (%)",
                line_shape='spline'
            )
            fig_evol.update_traces(line_color='#ef553b', line_width=4)
            st.plotly_chart(fig_evol, width='stretch')

        # 4. Tabela de Detalhes
        with st.expander("Ver ranking completo por jornal"):
            st.dataframe(indice_jornal[['jornal', 'Percentual (%)']], width='stretch', hide_index=True)

# import plotly.express as px
# import streamlit as st
# import pandas as pd

# class AnaliseClimatica:
#     def __init__(self, df_selecionado, colors):
#         """
#         df_selecionado: DataFrame principal
#         colors: Escala de cores do dashboard
#         """
#         self.df = df_selecionado
#         self.colors = colors

#     def renderizar(self):
#         st.header("🌍 Foco: Alterações Climáticas")

#         if 'climaticas' not in self.df.columns:
#             st.error("A coluna 'climaticas' não foi encontrada na base de dados.")
#             return

#         # 1. Preparação dos dados
#         df_cli = self.df.copy()
#         # Transformação para rótulos legíveis
#         df_cli['Status'] = df_cli['climaticas'].map({1: 'Sim', 0: 'Não'})
        
#         # 2. Métricas de Destaque (KPIs)
#         total_noticias = len(df_cli)
#         total_sim = df_cli['climaticas'].sum()
#         percentual = (total_sim / total_noticias * 100).round(1)

#         c1, c2, c3 = st.columns(3)
#         c1.metric("Total de Notícias", total_noticias)
#         c2.metric("Notícias sobre Clima", total_sim)
#         c3.metric("Representatividade", f"{percentual}%")

#         st.divider()

#         # 3. Análise Temporal e Proporcional
#         tab_proporcao, tab_evolucao = st.tabs(["📊 Proporção no Corpus", "📈 Evolução Temporal"])

#         with tab_proporcao:
#             # Gráfico de Rosca para o total
#             contagem = df_cli['Status'].value_counts().reset_index()
#             contagem.columns = ['Foco Climático', 'Total']
            
#             fig_pie = px.pie(
#                 contagem, 
#                 values='Total', 
#                 names='Foco Climático',
#                 hole=0.5,
#                 title="A pauta é sobre Alterações Climáticas?",
#                 color='Foco Climático',
#                 color_discrete_map={'Sim': '#ef553b', 'Não': '#636efa'} # Cores fixas para destaque
#             )
#             st.plotly_chart(fig_pie, width='stretch')

#         with tab_evolucao:
#             # Evolução por década
#             df_cli['Decada'] = (df_cli['Ano_Int'] // 10 * 10).astype(str) + "s"
            
#             # Agrupamento para calcular a % de notícias climáticas por década
#             evol_cli = df_cli.groupby(['Decada', 'Status']).size().unstack(fill_value=0)
#             # Garantir que a coluna 'Sim' exista para o cálculo
#             if 'Sim' not in evol_cli.columns:
#                 evol_cli['Sim'] = 0
                
#             evol_cli['%_Clima'] = (evol_cli['Sim'] / evol_cli.sum(axis=1) * 100).round(2)
#             evol_cli = evol_cli.reset_index()

#             fig_evol = px.line(
#                 evol_cli, 
#                 x='Decada', 
#                 y='%_Clima',
#                 markers=True,
#                 title="Crescimento da Temática Climática por Década (%)",
#                 labels={'%_Clima': 'Percentual do Corpus (%)', 'Decada': 'Década'},
#                 line_shape='spline'
#             )
#             fig_evol.update_traces(line_color='#ef553b', line_width=4)
#             st.plotly_chart(fig_evol, width='stretch')

#         # 4. Tabela de Detalhes
#         with st.expander("Ver dados detalhados por década"):
#             st.dataframe(evol_cli, width='stretch', hide_index=True)