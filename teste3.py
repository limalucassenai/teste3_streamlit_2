import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# =========================
# CONFIG INICIAL
# =========================
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")
st.title("📊 Dashboard de Vendas")

# =========================
# UPLOAD
# =========================
st.sidebar.header("📂 Upload de dados")

arquivo = st.sidebar.file_uploader("Envie seu CSV", type=["csv"])

caminho_padrao = "/home/lima-servidor/senai_semana_10/base_mobilidade_50000_linhas.csv"

@st.cache_data
def carregar_dados(fonte):
    df = pd.read_csv(fonte)

    # Tratamento de data
    if "data_venda" in df.columns:
        df["data_venda"] = pd.to_datetime(df["data_venda"], dayfirst=True, errors="coerce")

    return df

# Carregar dados
if arquivo:
    df = carregar_dados(arquivo)
else:
    df = carregar_dados(caminho_padrao)

# =========================
# PREVIEW
# =========================
with st.expander("🔍 Prévia dos dados"):
    st.dataframe(df.head())

# =========================
# FILTROS
# =========================
st.sidebar.header("⚙️ Filtros")

# Seleção coluna numérica
colunas_numericas = df.select_dtypes(include="number").columns

if len(colunas_numericas) == 0:
    st.error("Nenhuma coluna numérica encontrada.")
    st.stop()

coluna_valor = st.sidebar.selectbox("Coluna numérica", colunas_numericas)

# Slider numérico
valor_min, valor_max = st.sidebar.slider(
    "Filtrar valores",
    float(df[coluna_valor].min()),
    float(df[coluna_valor].max()),
    (float(df[coluna_valor].min()), float(df[coluna_valor].max()))
)

df_filtrado = df[
    (df[coluna_valor] >= valor_min) &
    (df[coluna_valor] <= valor_max)
]

# Filtro categórico (estado)
if "estado" in df.columns:
    estados = st.sidebar.multiselect(
        "Filtrar por estado",
        options=df["estado"].dropna().unique(),
        default=df["estado"].dropna().unique()
    )
    df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados)]

# =========================
# KPIs
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total registros", len(df_filtrado))

with col2:
    st.metric("Média", round(df_filtrado[coluna_valor].mean(), 2))

with col3:
    st.metric("Soma", round(df_filtrado[coluna_valor].sum(), 2))

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Distribuição",
    "📈 Interativo",
    "📂 Categóricos",
    "📅 Temporal"
])

# =========================
# TAB 1 - MATPLOTLIB
# =========================
with tab1:
    st.subheader("Distribuição (Matplotlib)")

    fig, ax = plt.subplots()
    ax.hist(df_filtrado[coluna_valor], bins=50)
    ax.set_title("Distribuição")
    ax.set_xlabel(coluna_valor)
    ax.set_ylabel("Frequência")

    st.pyplot(fig)

# =========================
# TAB 2 - PLOTLY
# =========================
with tab2:
    st.subheader("Distribuição Interativa")

    fig = px.histogram(
        df_filtrado,
        x=coluna_valor,
        nbins=50
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# TAB 3 - CATEGÓRICOS
# =========================
with tab3:
    st.subheader("Análises Categóricas")

    # Categoria
    if "categoria" in df.columns and "valor_total" in df.columns:

        categoria_agg = (
            df_filtrado
            .groupby("categoria")["valor_total"]
            .sum()
            .reset_index()
            .sort_values(by="valor_total", ascending=False)
        )

        fig_bar = px.bar(
            categoria_agg,
            x="categoria",
            y="valor_total",
            title="Faturamento por Categoria"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    # Estado
    if "estado" in df.columns:

        estado_agg = df_filtrado["estado"].value_counts().reset_index()
        estado_agg.columns = ["estado", "quantidade"]

        fig_estado = px.bar(
            estado_agg,
            x="estado",
            y="quantidade",
            title="Vendas por Estado"
        )

        st.plotly_chart(fig_estado, use_container_width=True)

# =========================
# TAB 4 - TEMPORAL
# =========================
with tab4:
    st.subheader("Evolução das Vendas")

    if "data_venda" in df.columns and "valor_total" in df.columns:

        df_tempo = (
            df_filtrado
            .groupby("data_venda")["valor_total"]
            .sum()
            .reset_index()
            .sort_values("data_venda")
        )

        fig = px.line(
            df_tempo,
            x="data_venda",
            y="valor_total",
            title="Evolução ao longo do tempo"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Colunas 'data_venda' ou 'valor_total' não encontradas")

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown("✅ Execute com: `streamlit run app.py`")