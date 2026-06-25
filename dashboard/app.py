import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
from dash import Dash, dcc, html

# Criando conexão com o banco de dados
engine = create_engine("postgresql://terralab:terralab123@postgres:5432/terralab_db")

# Lendo os dados da tabela "dados" do banco de dados
df = pd.read_sql("SELECT * FROM enderecos_dashboard", engine)

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

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

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

app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand = "TerraLab - Dashboard de Dados Geoespaciais",
        color = "primary",
        dark = True,
        className = "mb-4"
    ),

    dbc.Card([
        dbc.CardHeader("Mapa 1 - Pontos COloridos por geoapi_id"),
        dbc.CardBody(dcc.Graph(figure=fig_mapa1, style={"height":"600px"}))
    ], className = "mb-4"),

    dbc.Card([
        dbc.CardHeader("Mapa 2 - Pontos dentro/fora da unidade federativa"),
        dbc.CardBody(dcc.Graph(figure=fig_mapa2, style={"height":"600px"}))
    ], className = "mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Gráfico 3 - Quantidade de dados por mês"),
            dbc.CardBody(dcc.Graph(figure=fig_grafico3, style={"height":"400px"}))
        ]), width = 6),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Gráfico 4 - Top 3 cidades com mais dados"),
            dbc.CardBody(dcc.Graph(figure=fig_grafico4, style={"height":"400px"}))
        ]), width = 6),
    ])
], fluid=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=False)

