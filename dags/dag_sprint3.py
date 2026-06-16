from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
import json
from shapely.geometry import shape, Point

# ── Configuração do DAG ────────────────────────────────────────────────────────
default_args = {
    'owner': 'david souza',
    'start_date': datetime(2024, 6, 1),
    'retries': 1,
}

with DAG(
    dag_id='sprint3_etl_real',
    default_args=default_args,
    schedule_interval = None, # Sem agendamento automático
    catchup=False, # Não executar tarefas passadas
    description='ETL real: remover OpenRouteService e pontos fora da UF',

) as dag:
    # ── Tarefa 1: Extrair e filtrar o CSV ─────────────────────────────────────
    def extrair_filtrar_csv(**context):
        # Ler o CSV usando pandas
        df = pd.read_csv('/opt/airflow/data/dados_processo_seletivo.csv')
        #ler o arquivo completo agora
        #E agora vamos salvar como parquet. Parquet é um formato de arquivo colunar que é mais eficiente para leitura e escrita, além de ser compactado. Ele é amplamente utilizado em ambientes de big data e análise de dados.
        df.to_parquet('/opt/airflow/data/dados_processo_seletivo.parquet', index=False)
        # vamos printar quantas linhas tem o arquivo csv
        print(f"O arquivo CSV tem {len(df)} linhas.\n")
        print("APIs que estão no CSV:")
        print(df['geoapi_id'].unique())
        print(f"\nQuantidade de pontos para cada API:")
        print(df['geoapi_id'].value_counts())

    tarefa_extrair_filtrar = PythonOperator(
        task_id='extrair_filtrar_csv',
        python_callable=extrair_filtrar_csv,
    )

    def transformar_dados(**context):
        # 1. Ler o parquet gerado na tarefa anterior
        df = pd.read_parquet('/opt/airflow/data/dados_processo_seletivo.parquet')
        print(f"Linhas antes de filtrar: {len(df)}")
        # 2. remover as linhas onde a geoapi_id seja igual a "OpenRouteService"
        df = df[df['geoapi_id'] != 'OpenRouteService']
        print(f"Linhas após remover OpenRouteService: {len(df)}")
        # 3.A carregar os poligonos do arquivo json
        with open('/opt/airflow/data/br_states.json' , 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        
        # Olhar propriedades do primeiro estado para entender a estrutura do geojson
        print(f"Propriedades do GeoJSON:", geojson['features'][0]['properties'])

        estados_poligonos = {}
        for feature in geojson['features']:
            # sigla = feature['properties']['sigla'] -  Errei aqui pq é "SIGLA" em maiúsculo
            sigla = feature['properties']['SIGLA']
            estados_poligonos[sigla] = shape(feature['geometry'])
        
        print(f"Estados: {list(estados_poligonos.keys())}")

        #3.B checa se cada ponto está dentro do estado correspondente
        def ponto_dentro_estado(row):
            uf = row['state']
            if uf not in estados_poligonos:
                return True
            return Point(row['longitude'], row['latitude']).within(estados_poligonos[uf])
        
        mascara = df.apply(ponto_dentro_estado, axis=1)
        print(f"Pontos fora da UF removidos: {(~mascara).sum()}")
        df = df[mascara]
        print(f"Linhas após filtrar pontos fora da UF: {len(df)}")

        # 4. Salvar o resultado parcial como parquet
        df.to_parquet('/opt/airflow/data/dados_processo_seletivo_transformado.parquet', index=False)

    # ── Tarefa 2: Salvar no PostgreSQL ─────────────────────────────────
    def salvar_no_postgres(**context):
        # Recuperar os dados filtrados com XCom da tarefa anterior
        # dados_json = context['ti'].xcom_pull(key='dados_aracaju', task_ids='extrair_filtrar_csv')
        dados_json = pd.read_parquet('/opt/airflow/data/dados_processo_seletivo_transformado.parquet').to_json()
        df =  pd.read_json(dados_json)

        # Conecta no PostgreSQL usando a connection configurada no Airflow
        hook = PostgresHook(postgres_conn_id='postgres_default')
        engine = hook.get_sqlalchemy_engine()

        df.to_sql(
            name = 'enderecos_transformados_tratados',
            con = engine,
            if_exists = 'replace',
            index = False,
        )
        print("Dados salvos no PostgreSQL com sucesso!")

    tarefa_transformar_dados = PythonOperator(
        task_id='transformar_dados',
        python_callable=transformar_dados,
    )

    tarefa_salvar_postgres = PythonOperator(
        task_id='salvar_no_postgres',
        python_callable=salvar_no_postgres,
        provide_context=True, # Necessário para acessar o contexto e XCom
    )

        # define a ordem de execução das tarefas
    tarefa_extrair_filtrar >> tarefa_transformar_dados >> tarefa_salvar_postgres
    
