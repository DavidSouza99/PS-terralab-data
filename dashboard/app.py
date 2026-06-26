import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
# Imports:
#   Dash: É a classe principal para criar a aplicação
#   dcc: É o método de componentes interativos do Dash
#   html: É o método para componentes HTML no Dash
#   Input: É usado em Callbacks para ler valores de componentes
#   Output: É usado em Callbacks para atualizar componentes
#   callback: É o decorador que conecta Input e Output ao corpo da função
from dash import Dash, dcc, html, Input, Output, callback

# Criando conexão com o banco de dados
engine = create_engine("postgresql://terralab:terralab123@postgres:5432/terralab_db")

# Lendo os dados da tabela "dados" do banco de dados
df = pd.read_sql("SELECT * FROM enderecos_dashboard", engine)

#Métricas
total = len(df)
dentro = int(df['dentro_uf'].sum())
fora = total - dentro
apis = df['geoapi_id'].nunique()
top_cidade = df['city'].value_counts().index[0].title()

# Montando mapa 1
fig_mapa1 = px.scatter_mapbox(
    df,
    lat = "latitude",        # Coluna Latitude do DataFrame
    lon = "longitude",        # Coluna Longitude do DataFrame
    color = "geoapi_id",     # Queremos colorir os pontos de acordo com a coluna geoapi_id
    title = "Mapa 1 - Pontos coloridos por geoapi_id",
    zoom = 3,
    mapbox_style = "open-street-map" #mapa base gratuito
)

# Montando mapa 2
fig_mapa2 = px.scatter_mapbox(
    df,
    lat = "latitude",        # Coluna Latitude do DataFrame
    lon = "longitude",        # Coluna Longitude do DataFrame
    color = "dentro_uf",     # Queremos colorir os pontos de acordo com a coluna bairro
    color_discrete_map = {
        True: "green",
        False: "red"}, # Definindo cores para os valores da coluna bairro
    title = "Mapa 2 — Pontos dentro/fora da unidade federativa",
    zoom = 3,
    mapbox_style = "open-street-map" #mapa base gratuito
)

# Montando grafico 3 - Quantidade por mês
df['mes'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)  # Convertendo a coluna 'date' para período mensal
df_por_mes = df.groupby('mes').size().reset_index(name='quantidade')  # Agrupando por mês e contando a quantidade

fig_grafico3 = px.bar(
    df_por_mes,
    x='mes',
    y='quantidade',
    title='Gráfico 3 - Quantidade de dados por mês',
    labels={'mes': 'Mês', 'quantidade': 'Quantidade de Dados'}
)

df_top3 = df['city'].value_counts().head(3).reset_index()
# Colunas: 'index' (cidade) e 'city' (quantidade)

fig_grafico4 = px.bar(
    df_top3,
    x='city',
    y='count',
    title='Gráfico 4 - Top 3 cidades com mais dados',
    labels={'city': 'Cidade', 'count': 'Quantidade de Dados'}
)

# Utilizando o Dash para criar o dashboard

app = Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500&display=swap"
    ])

def metric_card(value, label):
    return html.Div([
        html.Span(str(value), className="metric-value"),
        html.Span(label, className="metric-label")
    ], className="metric-card")

# Dashboard sem estilo

#app.layout = html.Div([
#    html.H1("TerraLab - Dashboard de Dados Geoespaciais"),
#
#    html.H2("Mapa 1 - Pontos coloridos por geoapi_id"),
#    dcc.Graph(figure=fig_mapa1, style={"height":"600px"}),
#
#    html.H2("Mapa 2 - Pontos dentro/fora da unidade federativa"),
#    dcc.Graph(figure=fig_mapa2, style={"height":"600px"}),
#
#    html.H2("Gráfico 3 - Quantidade de dados por mês"),
#    dcc.Graph(figure=fig_grafico3, style={"height":"400px"}),
#
#    html.H2("Gráfico 4 - Top 3 cidades com mais dados"),
#    dcc.Graph(figure=fig_grafico4, style={"height":"400px"}),
#])

# Dashboard utilizando bootstrap FLATLY

app.layout = html.Div([
    #Header
    html.Div([
        html.P("TERRALAB · DATA ANALYTICS", className="header-coords"),
        html.H1("Análise de APIs de Geocodificação", className="header-title"),
        html.P("Comparativo de precisão entre MapBox, TomTom, Google e Here sobre endereços brasileiros — validação por unidade federativa.", className="header-subtitle"),
        html.Div([
            metric_card(f"{total:,}".replace(",","."), "Pontos Totais"),
            metric_card(f"{dentro:,}".replace(",","."), "Dentro da UF"),
            metric_card(fora, "Fora da UF"),
            metric_card(apis, "APIs utilizadas"),
            metric_card(top_cidade, "Top Cidades"),
        ], className="metrics-row"),
    ], className="header-section"),

    #Contruindo conteúdo com abas
    html.Div([
        dbc.Tabs([
            dbc.Tab(label="Mapa por API", tab_id="tab-1"),
            dbc.Tab(label="Dentro/Fora da UF", tab_id="tab-2"),
            dbc.Tab(label="Gráficos", tab_id="tab-3"),
        ], id="tabs", active_tab="tab-1"),
        html.Div(id="tab-content", className="tab-content-area"),
    ], className="content-section"),
])

@callback(Output("tab-content", "children"), Input("tabs", "active_tab"))

def render_tab(tab):
    if tab=="tab-1":
        return dcc.Graph(figure=fig_mapa1, style={"height":"600px"})
    elif tab=="tab-2":
        return dcc.Graph(figure=fig_mapa2, style={"height":"600px"})
    elif tab=="tab-3":
        return dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_grafico3, style={"height":"400px"}), width=6),
            dbc.Col(dcc.Graph(figure=fig_grafico4, style={"height":"400px"}), width=6),
        ])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=False)

