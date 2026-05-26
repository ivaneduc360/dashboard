import pandas as pd
import plotly.express as px
import sqlalchemy
import streamlit as st

# 1. Conexão com o Banco de Dados
# (Substitua com suas credenciais locais ou de produção)
engine = sqlalchemy.create_engine(
    "mysql+pymysql://usuario:senha@localhost/u798098636_aulas"
)


# 2. Funções para carregar dados
@st.cache_data
def carregar_dados_demograficos():
    query = """
    SELECT genero, COUNT(*) as qtd 
    FROM alunos 
    GROUP BY genero
    """
    return pd.read_sql(query, engine)


@st.cache_data
def carregar_frequencia():
    query = """
    SELECT data_aula, presente 
    FROM presencas
    """
    df = pd.read_sql(query, engine)
    df["data_aula"] = pd.to_datetime(df["data_aula"])
    return df


# 3. Construção do Dashboard no Streamlit
st.set_page_config(page_title="Dashboard Instituto Carisma", layout="wide")
st.title("📊 Painel de Análise Educacional e Impacto Social")

tab1, tab2 = st.tabs(["Visão Patrocinador", "Visão Pedagógica"])

with tab1:
    st.header("Impacto e Demografia dos Alunos")
    df_demografia = carregar_dados_demograficos()

    col1, col2 = st.columns(2)
    with col1:
        # Gráfico de Gênero
        fig_gen = px.pie(
            df_demografia,
            values="qtd",
            names="genero",
            title="Distribuição por Gênero",
        )
        st.plotly_chart(fig_gen)

    with col2:
        # Espaço para colocar o indicador de PCDs/Síndromes
        st.metric(label="Total de Alunos Atendidos", value=41)  # Exemplo estático
        st.metric(label="Projetos Ativos", value="Instituto Carisma")

with tab2:
    st.header("Engajamento e Frequência nas Aulas")
    df_freq = carregar_frequencia()

    # Agrupando por data para ver evolução da presença
    df_linha = df_freq.groupby("data_aula")["presente"].mean().reset_index()
    df_linha["presente"] = df_linha["presente"] * 100

    fig_linha = px.line(
        df_linha,
        x="data_aula",
        y="presente",
        title="Evolução da Taxa de Presença (%)",
        labels={"presente": "Presença Média (%)", "data_aula": "Data da Aula"},
    )
    st.plotly_chart(fig_linha)
