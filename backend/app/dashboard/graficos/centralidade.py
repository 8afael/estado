from scipy import stats
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from graficos import cores

class Centralidade:
    def __init__(self, df, colors):
        """
        Inicia a classe com o dataframe e a paleta de cores padrão.
        """
        self.df = df
        self.colors = colors
        self.COL_TAMANHO = 'palavras'
        self.bootstrap_colors = ["#0d6efd", "#6c757d", "#198754", "#dc3545", "#ffc107", "#0dcaf0"]
        

    def renderizar(self):
        st.header("📝 Evolução da Extensão e Centralidade Jornalística")
        
        if self.COL_TAMANHO not in self.df.columns:
            st.error(f"A coluna '{self.COL_TAMANHO}' não foi encontrada no banco de dados. Por favor, verifique o nome da variável de extensão.")
        else:
            # Estatísticas Descritivas por Ano
            #df_stats = df.groupby('Ano_Int')[COL_TAMANHO].agg(['mean', 'median', 'std', 'count']).reset_index()
            
            df_stats_jornal = self.df.groupby(['Ano_Int', 'jornal'])[self.COL_TAMANHO].agg(['mean', 'median', 'std', 'count']).reset_index()  
            
            # 1. Gráfico de Linha com Tendência (Inferencial)
            st.subheader("📈 Tendência Temporal do Tamanho por Jornal")

            fig_ext = go.Figure()

            # Lista de jornais únicos para iterar
            lista_jornais = df_stats_jornal['jornal'].unique()

            for i, jr in enumerate(lista_jornais):
                # Filtrar dados apenas deste jornal
                df_jr = df_stats_jornal[df_stats_jornal['jornal'] == jr]
                
                if len(df_jr) > 1:
                    # Cálculo da Regressão para cada jornal individualmente
                    slope, intercept, r_value, p_value, std_err = stats.linregress(df_jr['Ano_Int'], df_jr['mean'])
                    reg_line = slope * df_jr['Ano_Int'] + intercept
                    
                    # Cor correspondente ao jornal (usando a sua lista bootstrap_colors)
                    #cor = self.bootstrap_colors[i % len(self.bootstrap_colors)]
                    cor = cores.CORES_JORNAIS.get(jr, "#e4121b")
                    
                    # Adiciona a linha da Média (Sólida)
                    fig_ext.add_trace(go.Scatter(
                        x=df_jr['Ano_Int'], y=df_jr['mean'],
                        mode='lines+markers',
                        name=f'Média: {jr}',
                        line=dict(color=cor, width=2)
                    ))
                    
                    # Adiciona a Linha de Tendência (Tracejada)
                    fig_ext.add_trace(go.Scatter(
                        x=df_jr['Ano_Int'], y=reg_line,
                        mode='lines',
                        name=f'Tendência: {jr} (p={p_value:.3f})',
                        line=dict(color=cor, dash='dot', width=1),
                        showlegend=True
                    ))

            fig_ext.update_layout(
                yaxis_title="Extensão (Palavras)",
                xaxis_title="Ano",
                legend_title="Jornais e Tendências",
                hovermode="x unified"
            )
            st.plotly_chart(fig_ext, width='stretch')


            # 2. Boxplots por Década e Jornal
            st.divider()
            st.subheader("📦 Distribuição e Variabilidade (Quartis e Outliers)")
            fig_box = px.box(self.df, x='Década', y=self.COL_TAMANHO, color='jornal', color_discrete_map=cores.CORES_JORNAIS, points="outliers", title="Comparação de Extensão por Década e Jornal")
            fig_box.update_layout(xaxis_title="Década", yaxis_title="Tamanho")
            st.plotly_chart(fig_box, width='stretch')

            # 3. Painel de Estatísticas Inferencial
            st.divider()
            c_est1, c_est2, c_est3 = st.columns(3)
            with c_est1:
                st.metric("Significância (p-value)", f"{p_value:.4f}")
                if p_value < 0.05: st.success("Tendência Significativa")
                else: st.warning("Sem Significância Estatística")
            with c_est2:
                st.metric("Correlação (R²)", f"{r_value**2:.3f}")
            with c_est3:
                st.metric("Taxa de Crescimento", f"{slope:.2f} unid/ano")
                
            st.info(f"💡 **Interpretação:** Um p-value abaixo de 0.05 e um slope positivo indicam que o tema ambiental não só aumentou em frequência, mas também em profundidade (centralidade), ocupando mais espaço nos jornais ao longo dos 50 anos.")
