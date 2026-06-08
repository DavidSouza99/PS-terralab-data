from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd

# ── Configuração do DAG ────────────────────────────────────────────────────────
default_args = {
    'owner': 'david souza',
    'start_date': datetime(2024, 6, 1),
    'retries': 1,
}

with DAG(
    dag_id='sprint2_aracaju_etl',
    default_args=default_args,
    schedule_interval = None, # Sem agendamento automático
    catchup=False, # Não executar tarefas passadas
    description='Importar CSV e salvar endereços de Aracaju no PostgreSQL',
) as dag:
    # ── Tarefa 1: Extrair e filtrar o CSV ─────────────────────────────────────
    def extrair_filtrar_csv(**context):
        # Ler o CSV usando pandas
        df = pd.read_csv('/opt/airflow/data/dados_processo_seletivo.csv')
        # Filtrar apenas os endereços de Aracaju
        df_aracaju = df[df['city'] == 'ARACAJU']
        print(f"Endereços de Aracaju encontrados: {len(df_aracaju)}")
        # Passar o DataFrame filtrado para a próxima tarefa usando XCom
        context['ti'].xcom_push(key='dados_aracaju', value=df_aracaju.to_json())

    tarefa_extrair_filtrar = PythonOperator(
        task_id='extrair_filtrar_csv',
        python_callable=extrair_filtrar_csv,
    )

    # ── Tarefa 2: Salvar no PostgreSQL ─────────────────────────────────
    def salvar_no_postgres(**context):
        # Recuperar os dados filtrados com XCom da tarefa anterior
        dados_json = context['ti'].xcom_pull(key='dados_aracaju', task_ids='extrair_filtrar_csv')
        df =  pd.read_json(dados_json)

        # Conecta no PostgreSQL usando a connection configurada no Airflow
        hook = PostgresHook(postgres_conn_id='postgres_default')
        engine = hook.get_sqlalchemy_engine()

        df.to_sql(
            name = 'enderecos_aracaju',
            con = engine,
            if_exists = 'replace',
            index = False,
        )
        print("Dados salvos no PostgreSQL com sucesso!")

    tarefa_salvar_postgres = PythonOperator(
        task_id='salvar_no_postgres',
        python_callable=salvar_no_postgres,
        provide_context=True, # Necessário para acessar o contexto e XCom
    )

        # define a ordem de execução das tarefas
    tarefa_extrair_filtrar >> tarefa_salvar_postgres
    
