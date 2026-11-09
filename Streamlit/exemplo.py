from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="IDH", layout="wide")

DATA_FILE = Path(__file__).with_name("Tabela4.csv")
UFS_CONSORCIO = ["MA", "PA", "AC", "BA", "MG"]
COMPONENTES = ["IDHM geral", "Longevidade", "Educação", "Renda"]
CORES = ["#315c8c", "#4c8c7a", "#b7813e", "#8d6a9f", "#c45b50"]


@st.cache_data
def carregar_dados(caminho: str) -> pd.DataFrame:
    dados = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin-1",
        skiprows=1,
        decimal=",",
    )
    anos = [coluna for coluna in dados.columns if str(coluna).isdigit()]
    if not anos:
        raise ValueError("Não foram encontradas colunas de anos no arquivo.")

    dados = dados.rename(columns={dados.columns[0]: "UF", dados.columns[2]: "Estado"})
    for ano in anos:
        dados[ano] = pd.to_numeric(dados[ano], errors="coerce")

    return dados[["UF", "Estado", *anos]].dropna(subset=["UF", "Estado"])


def formatar_idhm(valor: float) -> str:
    return f"{valor:.3f}".replace(".", ",")


try:
    df = carregar_dados(str(DATA_FILE))
except (OSError, pd.errors.ParserError, ValueError) as erro:
    st.error(f"Não foi possível carregar Tabela4.csv: {erro}")
    st.stop()

anos_disponiveis = sorted(int(coluna) for coluna in df.columns if coluna.isdigit())
ufs_disponiveis = df["UF"].tolist()
ufs_iniciais = [uf for uf in UFS_CONSORCIO if uf in ufs_disponiveis]

with st.sidebar:
    st.header("Filtros")
    componente = st.selectbox("Componente do IDH", COMPONENTES)
    ufs_selecionadas = st.multiselect(
        "Estados",
        options=ufs_disponiveis,
        default=ufs_iniciais,
        format_func=lambda uf: f"{uf} — {df.loc[df['UF'] == uf, 'Estado'].iloc[0]}",
    )
    inicio_padrao = 2000 if 2000 in anos_disponiveis else anos_disponiveis[0]
    periodo = st.select_slider(
        "Período",
        options=anos_disponiveis,
        value=(inicio_padrao, anos_disponiveis[-1]),
    )

if not ufs_selecionadas:
    st.info("Selecione ao menos um estado.")
    st.stop()

colunas_ano = [str(ano) for ano in anos_disponiveis if periodo[0] <= ano <= periodo[1]]
if not colunas_ano:
    st.warning("Não há dados no período selecionado.")
    st.stop()

if componente != "IDHM geral":
    st.info(
        f"Tabela4.csv contém somente o IDHM geral. "
        f"Os valores de {componente} não estão disponíveis."
    )

recorte = df[df["UF"].isin(ufs_selecionadas)].copy()
ano_inicial, ano_final = colunas_ano[0], colunas_ano[-1]
serie = recorte.melt(
    id_vars=["UF", "Estado"],
    value_vars=colunas_ano,
    var_name="Ano",
    value_name="IDHM",
)
serie["Ano"] = serie["Ano"].astype(int)
valores_atuais = recorte[["UF", "Estado", ano_final]].rename(
    columns={ano_final: "IDHM"}
).dropna(subset=["IDHM"])
variacao = recorte[ano_final] - recorte[ano_inicial]

st.title("IDH")
st.caption(
    f"Comparação dos estados do consórcio. Dados disponíveis de {ano_inicial} a {ano_final}."
)

media = valores_atuais["IDHM"].mean()
iqr = valores_atuais["IDHM"].quantile(0.75) - valores_atuais["IDHM"].quantile(0.25)
desvio = valores_atuais["IDHM"].std(ddof=0)

kpis = st.columns(4)
kpis[0].metric(f"Média do IDHM · {ano_final}", formatar_idhm(media))
kpis[1].metric(
    f"Variação média · {ano_inicial}–{ano_final}",
    formatar_idhm(variacao.mean()),
)
kpis[2].metric("IQR entre estados", formatar_idhm(iqr))
kpis[3].metric("Desvio-padrão", formatar_idhm(desvio))

st.caption(
    f"Maior IDHM no recorte: {valores_atuais.loc[valores_atuais['IDHM'].idxmax(), 'Estado']} "
    f"({formatar_idhm(valores_atuais['IDHM'].max())}). "
    f"Menor: {valores_atuais.loc[valores_atuais['IDHM'].idxmin(), 'Estado']} "
    f"({formatar_idhm(valores_atuais['IDHM'].min())})."
)

st.subheader("Evolução do IDHM")
grafico_linha = px.line(
    serie,
    x="Ano",
    y="IDHM",
    color="Estado",
    markers=True,
    line_shape="linear",
    color_discrete_sequence=CORES,
    hover_name="Estado",
    hover_data={"UF": True, "Ano": True, "IDHM": ":.3f"},
)
grafico_linha.update_layout(
    template="plotly_white",
    height=390,
    margin={"l": 10, "r": 10, "t": 20, "b": 10},
    legend={"orientation": "h", "y": -0.2},
    xaxis={"dtick": 2, "title": "Ano"},
    yaxis={"range": [0.3, 1], "title": "IDHM"},
)
st.plotly_chart(grafico_linha, width="stretch")

coluna_radar, coluna_dispersao = st.columns(2)
with coluna_radar:
    st.subheader("Dimensões do IDHM")
    st.caption("Longevidade, Educação e Renda")
    st.info(
        "A tabela não informa os subíndices por dimensão. "
        "Por isso, não é possível montar o gráfico de radar ou apontar qual dimensão "
        "reduz mais o índice em cada estado."
    )

with coluna_dispersao:
    st.subheader("IDH inicial e variação")
    st.caption("A tabela não inclui valores de investimento público.")
    dados_dispersao = recorte[["UF", "Estado", ano_inicial, ano_final]].copy()
    dados_dispersao["Variação do IDH"] = (
        dados_dispersao[ano_final] - dados_dispersao[ano_inicial]
    )
    grafico_dispersao = px.scatter(
        dados_dispersao,
        x=ano_inicial,
        y="Variação do IDHM",
        color="Estado",
        color_discrete_sequence=CORES,
        hover_name="Estado",
        hover_data={"UF": True, ano_inicial: ":.3f", "Variação do IDHM": ":.3f"},
        title="IDHM no início do período e variação",
    )
    grafico_dispersao.update_traces(marker={"size": 12})
    grafico_dispersao.update_layout(
        template="plotly_white",
        height=330,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        showlegend=False,
        xaxis={"title": f"IDHM em {ano_inicial}"},
        yaxis={"title": "Variação do IDHM"},
    )
    st.plotly_chart(grafico_dispersao, width="stretch")

st.subheader(f"Comparação entre estados · {ano_final}")
ranking = px.bar(
    valores_atuais.sort_values("IDHM"),
    x="IDHM",
    y="Estado",
    text="IDHM",
    color="IDHM",
    color_continuous_scale=["#c45b50", "#e0b45d", "#4c8c7a"],
    hover_data={"UF": True, "IDHM": ":.3f"},
)
ranking.update_traces(texttemplate="%{text:.3f}", textposition="outside", cliponaxis=False)
ranking.update_layout(
    template="plotly_white",
    height=max(320, 36 * len(valores_atuais) + 80),
    margin={"l": 10, "r": 35, "t": 10, "b": 10},
    coloraxis_showscale=False,
    xaxis={"range": [0, 1], "title": "IDH"},
    yaxis={"title": ""},
)
st.plotly_chart(ranking, width="stretch")

st.subheader("Programas e notícias")
st.markdown(
    "- [Brasil Sem Fome](https://www.gov.br/mds/pt-br/acoes-e-programas/brasil-sem-fome)\n"
    "- [Bolsa Família](https://www.gov.br/mds/pt-br/acoes-e-programas/bolsa-familia)\n"
    "- [Notícias do Ministério do Desenvolvimento e Assistência Social](https://www.gov.br/mds/pt-br/noticias-e-conteudos)"
)

st.caption(
    "Fonte dos gráficos: Tabela4.csv (IDH total por UF). "
    "A análise municipal, as dimensões do IDH e os dados de investimento "
    "dependem de outras bases."
)
