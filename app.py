import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Anomalias - LOF",
    page_icon="⚡",
    layout="wide"
)

# =========================
# Funções auxiliares
# =========================

@st.cache_data
def carregar_dados(arquivo=None):
    """
    Carrega o arquivo de resultados gerado no Google Colab.
    O arquivo esperado é: resultado_anomalias_lof_energia.csv
    """
    if arquivo is not None:
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_csv("resultado_anomalias_lof_energia.csv")

    if "DataHora" in df.columns:
        df["DataHora"] = pd.to_datetime(df["DataHora"], errors="coerce")

    return df


def formatar_percentual(valor):
    return f"{valor:.2f}%"


# =========================
# Barra lateral
# =========================

st.sidebar.title("⚙️ Filtros")

st.sidebar.markdown(
    """
    Use os filtros abaixo para analisar os registros normais e anômalos
    identificados pelo algoritmo LOF.
    """
)

arquivo_upload = st.sidebar.file_uploader(
    "Enviar arquivo CSV gerado no Colab",
    type=["csv"]
)

# =========================
# Carregamento dos dados
# =========================

try:
    if arquivo_upload is not None:
        df = carregar_dados(arquivo_upload)
    else:
        df = carregar_dados()

except FileNotFoundError:
    st.title("⚡ Dashboard de Detecção de Anomalias no Consumo de Energia")

    st.warning(
        """
        Nenhum arquivo de dados foi encontrado.

        Para usar este dashboard, coloque o arquivo
        `resultado_anomalias_lof_energia.csv` na mesma pasta do `app.py`
        ou envie o arquivo pela barra lateral.
        """
    )

    st.stop()


# =========================
# Validação básica
# =========================

colunas_obrigatorias = ["Classe", "Score_Anomalia"]

for coluna in colunas_obrigatorias:
    if coluna not in df.columns:
        st.error(f"A coluna obrigatória `{coluna}` não foi encontrada no arquivo.")
        st.stop()


# =========================
# Título e descrição
# =========================

st.title("⚡ Dashboard de Detecção de Anomalias no Consumo de Energia Elétrica")

st.markdown(
    """
    Este dashboard apresenta uma aplicação de **detecção de anomalias** em dados
    de consumo de energia elétrica. O objetivo é identificar registros com
    comportamento diferente do padrão observado na base de dados.

    O algoritmo utilizado foi o **Local Outlier Factor (LOF)**, um método de
    aprendizado de máquina não supervisionado que detecta anomalias com base
    na densidade local dos registros.
    """
)

st.divider()


# =========================
# Filtros
# =========================

classes_disponiveis = sorted(df["Classe"].dropna().unique())

classe_filtro = st.sidebar.multiselect(
    "Filtrar por classe",
    options=classes_disponiveis,
    default=classes_disponiveis
)

df_filtrado = df[df["Classe"].isin(classe_filtro)].copy()

if "DataHora" in df.columns and df["DataHora"].notna().sum() > 0:
    data_min = df["DataHora"].min().date()
    data_max = df["DataHora"].max().date()

    intervalo_datas = st.sidebar.date_input(
        "Filtrar por período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max
    )

    if isinstance(intervalo_datas, tuple) and len(intervalo_datas) == 2:
        inicio, fim = intervalo_datas

        df_filtrado = df_filtrado[
            (df_filtrado["DataHora"].dt.date >= inicio) &
            (df_filtrado["DataHora"].dt.date <= fim)
        ]


colunas_numericas = df.select_dtypes(include="number").columns.tolist()

colunas_para_grafico = [
    coluna for coluna in colunas_numericas
    if coluna not in ["Anomalia", "Score_Anomalia", "PCA1", "PCA2"]
]

if len(colunas_para_grafico) >= 2:
    eixo_x = st.sidebar.selectbox(
        "Eixo X do gráfico de dispersão",
        options=colunas_para_grafico,
        index=0
    )

    eixo_y = st.sidebar.selectbox(
        "Eixo Y do gráfico de dispersão",
        options=colunas_para_grafico,
        index=1
    )
else:
    eixo_x = None
    eixo_y = None


# =========================
# Informações do dataset
# =========================

st.header("1. Informações sobre o Dataset")

col1, col2, col3, col4 = st.columns(4)

total_registros = len(df)
total_filtrado = len(df_filtrado)
total_anomalias = len(df[df["Classe"] == "Anomalia"])
total_normais = len(df[df["Classe"] == "Normal"])

percentual_anomalias = (total_anomalias / total_registros) * 100 if total_registros > 0 else 0

col1.metric("Total de registros", total_registros)
col2.metric("Registros filtrados", total_filtrado)
col3.metric("Anomalias detectadas", total_anomalias)
col4.metric("Percentual de anomalias", formatar_percentual(percentual_anomalias))

st.markdown(
    """
    O dataset utilizado contém medições relacionadas ao consumo de energia elétrica.
    A partir dessas informações, o modelo LOF classifica os registros como
    **Normais** ou **Anomalias**.
    """
)

with st.expander("Visualizar primeiras linhas do dataset"):
    st.dataframe(df.head(20), use_container_width=True)


# =========================
# Algoritmo
# =========================

st.header("2. Algoritmo Utilizado")

st.markdown(
    """
    O algoritmo escolhido foi o **Local Outlier Factor (LOF)**.

    O LOF compara cada registro com seus vizinhos mais próximos. Quando um
    registro está em uma região com baixa densidade, ou seja, distante do padrão
    dos demais registros, ele pode ser classificado como uma anomalia.

    Neste projeto, registros classificados como **Anomalia** representam possíveis
    momentos de consumo elétrico fora do comportamento comum da residência.
    """
)


# =========================
# Análise exploratória
# =========================

st.header("3. Análise Exploratória dos Dados")

if "Global_active_power" in df_filtrado.columns:
    fig_hist = px.histogram(
        df_filtrado,
        x="Global_active_power",
        color="Classe",
        nbins=50,
        title="Distribuição do Consumo Global de Energia"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    fig_box = px.box(
        df_filtrado,
        x="Classe",
        y="Global_active_power",
        title="Boxplot do Consumo Global de Energia por Classe"
    )
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.info("A coluna `Global_active_power` não foi encontrada no arquivo.")


if "DataHora" in df_filtrado.columns and "Global_active_power" in df_filtrado.columns:
    st.subheader("Consumo de Energia ao Longo do Tempo")

    fig_linha = px.line(
        df_filtrado.sort_values("DataHora"),
        x="DataHora",
        y="Global_active_power",
        color="Classe",
        title="Variação do Consumo de Energia no Tempo"
    )

    st.plotly_chart(fig_linha, use_container_width=True)


# =========================
# Visualização das anomalias
# =========================

st.header("4. Visualização das Anomalias Detectadas")

if eixo_x is not None and eixo_y is not None:
    fig_scatter = px.scatter(
        df_filtrado,
        x=eixo_x,
        y=eixo_y,
        color="Classe",
        hover_data=["Score_Anomalia"],
        title=f"Dispersão entre {eixo_x} e {eixo_y}"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("Não há colunas numéricas suficientes para gerar o gráfico de dispersão.")


if "PCA1" in df_filtrado.columns and "PCA2" in df_filtrado.columns:
    st.subheader("Visualização com PCA")

    fig_pca = px.scatter(
        df_filtrado,
        x="PCA1",
        y="PCA2",
        color="Classe",
        hover_data=["Score_Anomalia"],
        title="Visualização dos Registros com PCA"
    )

    st.plotly_chart(fig_pca, use_container_width=True)


# =========================
# Métricas e indicadores
# =========================

st.header("5. Métricas e Indicadores")

score_medio_geral = df["Score_Anomalia"].mean()

if total_anomalias > 0:
    score_medio_anomalias = df[df["Classe"] == "Anomalia"]["Score_Anomalia"].mean()
else:
    score_medio_anomalias = 0

if total_normais > 0:
    score_medio_normais = df[df["Classe"] == "Normal"]["Score_Anomalia"].mean()
else:
    score_medio_normais = 0

m1, m2, m3 = st.columns(3)

m1.metric("Score médio geral", f"{score_medio_geral:.4f}")
m2.metric("Score médio dos normais", f"{score_medio_normais:.4f}")
m3.metric("Score médio das anomalias", f"{score_medio_anomalias:.4f}")

st.markdown(
    """
    O **Score de Anomalia** indica o quanto um registro se diferencia do padrão
    dos demais dados. Quanto maior o score, maior a possibilidade de o registro
    representar um comportamento atípico.
    """
)


# =========================
# Tabela de anomalias
# =========================

st.header("6. Tabela com Registros Anômalos")

anomalias = df_filtrado[df_filtrado["Classe"] == "Anomalia"].copy()

if len(anomalias) > 0:
    anomalias = anomalias.sort_values("Score_Anomalia", ascending=False)

    st.dataframe(anomalias, use_container_width=True)

    csv_anomalias = anomalias.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Baixar tabela de anomalias em CSV",
        data=csv_anomalias,
        file_name="anomalias_filtradas.csv",
        mime="text/csv"
    )
else:
    st.info("Nenhuma anomalia encontrada com os filtros atuais.")


# =========================
# Interpretação prática
# =========================

st.header("7. Interpretação das Anomalias")

st.markdown(
    """
    As anomalias detectadas representam registros em que o consumo de energia
    elétrica apresentou comportamento diferente do padrão observado na base.

    Na prática, esses registros podem indicar:

    - picos de consumo de energia;
    - uso simultâneo de vários equipamentos elétricos;
    - falhas ou ruídos na medição;
    - situações incomuns de consumo;
    - possíveis desperdícios ou eventos fora da rotina.

    Como se trata de um método não supervisionado, o algoritmo não afirma
    automaticamente que existe um problema real. Ele apenas aponta registros
    que merecem uma análise mais detalhada.
    """
)


# =========================
# Conclusão
# =========================

st.header("8. Conclusão")

st.markdown(
    f"""
    A aplicação permitiu identificar **{total_anomalias} registros anômalos**,
    correspondendo a aproximadamente **{percentual_anomalias:.2f}%** da base
    analisada.

    O uso do algoritmo LOF mostrou-se adequado para este projeto, pois permite
    detectar registros fora do padrão com base na densidade local dos dados.
    Dessa forma, o dashboard facilita a visualização, a análise e a interpretação
    dos possíveis comportamentos anormais de consumo de energia elétrica.
    """
)