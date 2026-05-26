import urllib.parse
import pandas as pd
import plotly.express as px
import sqlalchemy
import streamlit as st

# ==============================================================================
# 1. CONEXÃO COM O BANCO DE DADOS (Configuração Segura)
# ==============================================================================

# Dados de acesso fornecidos
usuario = "u798098636_aulas"
senha_original = "@#Fab001122@#"
servidor = "srv1883.hstgr.io"
porta = "3306"
banco = "u798098636_aulas"

# Transforma os caracteres especiais (@, #) em texto seguro para URL (URL Encoding)
senha_codificada = urllib.parse.quote_plus(senha_original)

# Monta a string de conexão final perfeitamente estruturada
DATABASE_URL = (
    f"mysql+pymysql://{usuario}:{senha_codificada}@{servidor}:{porta}/{banco}"
)

# Cria o motor de conexão do SQLAlchemy
engine = sqlalchemy.create_engine(DATABASE_URL)


# ==============================================================================
# 2. FUNÇÕES PARA CARREGAR DADOS (Com Cache para Performance)
# ==============================================================================


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


# ==============================================================================
# 3. CONSTRUÇÃO DO DASHBOARD NO STREAMLIT
# ==============================================================================

st.set_page_config(page_title="Dashboard Instituto Carisma", layout="wide")
st.title("📊 Painel de Análise Educacional e Impacto Social")

# Criação das abas de navegação
tab1, tab2 = st.tabs(["Visão Patrocinador", "Visão Pedagógica"])

# --- ABA 1: VISÃO PATROCINADOR ---
with tab1:
    st.header("Impacto e Demografia dos Alunos")

    try:
        df_demografia = carregar_dados_demograficos()

        col1, col2 = st.columns(2)
        with col1:
            # Gráfico de Gênero
            fig_gen = px.pie(
                df_demografia,
                values="qtd",
                names="genero",
                title="Distribuição por Gênero",
                hole=0.4,  # Transforma em gráfico de rosca para ficar mais moderno
            )
            st.plotly_chart(fig_gen, use_container_width=True)

        with col2:
            # Indicadores de Impacto Social
            st.metric(label="Total de Alunos Atendidos", value=41)
            st.metric(label="Projetos Ativos", value="Instituto Carisma")

    except Exception as e:
        st.error(f"Erro ao carregar dados demográficos: {e}")

# --- ABA 2: VISÃO PEDAGÓGICA ---
with tab2:
    st.header("Engajamento e Frequência nas Aulas")

    try:
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
            markers=True,  # Adiciona pontinhos na linha do tempo
        )
        st.plotly_chart(fig_linha, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados de frequência: {e}")
