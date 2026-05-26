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
servidor = "193.203.175.217"
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
# 2. FUNÇÕES DE CARREGAMENTO (Métricas Globais e Listagens)
# ==============================================================================
@st.cache_data
def carregar_metricas_globais():
    # Busca o total de cadastros de cada entidade essencial
    qtd_alunos = pd.read_sql("SELECT COUNT(*) as total FROM alunos", engine).iloc[
        0
    ]["total"]
    qtd_turmas = pd.read_sql("SELECT COUNT(*) as total FROM turmas", engine).iloc[
        0
    ]["total"]
    qtd_cursos = pd.read_sql("SELECT COUNT(*) as total FROM cursos", engine).iloc[
        0
    ]["total"]
    qtd_aulas = pd.read_sql("SELECT COUNT(*) as total FROM aulas", engine).iloc[
        0
    ]["total"]
    return qtd_alunos, qtd_turmas, qtd_cursos, qtd_aulas


@st.cache_data
def carregar_detalhe_alunos():
    query = """
    SELECT 
        a.id AS `ID`,
        a.nome AS `Nome do Aluno`,
        a.genero AS `Gênero`,
        n.nome AS `Nível Escolar`,
        p.nome AS `Condição PCD`,
        s.nome AS `Síndrome`
    FROM alunos a
    LEFT JOIN niveis n ON a.nivel_id = n.id
    LEFT JOIN pcd p ON a.pcd_id = p.id
    LEFT JOIN sindromes s ON a.sindrome_id = s.id
    ORDER BY a.nome ASC
    """
    return pd.read_sql(query, engine)


@st.cache_data
def carregar_detalhe_turmas():
    query = """
    SELECT 
        t.id AS `ID Turma`,
        t.nome AS `Nome da Turma`,
        i.nome AS `Instrutor Responsável`,
        COUNT(ta.aluno_id) AS `Total de Alunos`
    FROM turmas t
    LEFT JOIN instrutores i ON t.instrutor_id = i.id
    LEFT JOIN turma_aluno ta ON t.id = ta.turma_id
    GROUP BY t.id
    ORDER BY t.nome ASC
    """
    return pd.read_sql(query, engine)


@st.cache_data
def carregar_detalhe_cursos():
    query = """
    SELECT 
        c.id AS `ID Curso`,
        c.nome AS `Nome do Curso`,
        COUNT(ca.aula_id) AS `Total de Aulas Vinculadas`
    FROM cursos c
    LEFT JOIN curso_aula ca ON c.id = ca.curso_id
    GROUP BY c.id
    ORDER BY c.nome ASC
    """
    return pd.read_sql(query, engine)


# ==============================================================================
# 3. INTERFACE INTERATIVA DO STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Gestão Instituto Carisma", layout="wide", page_icon="📊"
)

st.title("📊 Painel de Controle Operacional")
st.markdown("Visão geral de cadastros, gerenciamento de turmas e componentes.")

try:
    # 1. Carrega os grandes números (Cards)
    tot_alunos, tot_turmas, tot_cursos, tot_aulas = carregar_metricas_globais()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label="👥 Total de Alunos", value=int(tot_alunos))
    c2.metric(label="🏫 Turmas Ativas", value=int(tot_turmas))
    c3.metric(label="📚 Cursos na Grade", value=int(tot_cursos))
    c4.metric(label="📝 Aulas Registradas", value=int(tot_aulas))

    st.divider()

    # 2. Criação das Abas para Visualização das Tabelas Detalhadas
    st.subheader("🗂️ Consulta Avançada de Entidades")
    menu_abas = st.tabs(["Alunos", "Turmas", "Cursos & Grade Curricular"])

    # --- ABA: ALUNOS ---
    with menu_abas[0]:
        st.markdown("### Lista Geral de Alunos e Mapeamento de Inclusão")
        df_alunos = carregar_detalhe_alunos()

        # Filtro de busca textual rápido por aluno
        busca_aluno = st.text_input("🔍 Buscar aluno por nome:", "")
        if busca_aluno:
            df_alunos = df_alunos[
                df_alunos["Nome do Aluno"].str.contains(
                    busca_aluno, case=False, na=False
                )
            ]

        st.dataframe(df_alunos, use_container_width=True, hide_index=True)
        st.caption(f"Exibindo {len(df_alunos)} alunos cadastrados.")

    # --- ABA: TURMAS ---
    with menu_abas[1]:
        st.markdown("### Distribuição de Turmas e Professores")
        df_turmas = carregar_detalhe_turmas()
        st.dataframe(df_turmas, use_container_width=True, hide_index=True)

    # --- ABA: CURSOS ---
    with menu_abas[2]:
        st.markdown("### Cursos Disponíveis e Matriz Curricular")
        df_cursos = carregar_detalhe_cursos()
        st.dataframe(df_cursos, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro ao processar as consultas no banco de dados: {e}")
    except Exception as e:
        st.error(f"Erro ao carregar dados de frequência: {e}")
