# TerraLab — Processo Seletivo · Data Analytics

Repositório do processo seletivo para o time de **Data Analytics** do TerraLab - Universidade Federal de Ouro Preto (UFOP).

O projeto tem como propósito introduzir o aluno de forma prática e progressiva ao universo da Ciência de Dados.

Ao final das 5 sprints, o trainee será capaz de compreender e aplicar os principais conceitos, ferramentas e etapas do processo de análise de dados — desde a extração e transformação (ETL) até a visualização e comunicação dos resultados em dashboards interativos.  

---

## Trainee

**David Souza do Nascimento** · [@DavidSouza99](https://github.com/DavidSouza99) · david.nascimento@aluno.ufop.br

---

## Sprint 1 — Ambiente com Docker

Criação do ambiente isolado e reproduzível com Docker Compose, contendo os serviços de orquestração (Airflow) e banco de dados (PostgreSQL).

### Serviços

| Serviço | Imagem | Função |
|---------|--------|--------|
| `postgres` | postgres:15 | Banco de dados intermediário |
| `airflow-webserver` | apache/airflow:2.9.1 | Interface web — http://localhost:8080 |
| `airflow-scheduler` | apache/airflow:2.9.1 | Agendador de DAGs |

### Como executar

**Pré-requisito:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando.

```bash
# 1. Clone o repositório
git clone https://github.com/DavidSouza99/PS-terralab-data.git
cd PS-terralab-data

# O arquivo .env estão com minhas credenciais.

# 2. Inicialize o Airflow (rode uma vez)
docker compose up airflow-init

# 3. Suba o ambiente
docker compose up -d

# 4. Verifique se tudo está healthy
docker compose ps
# Você pode notar pela coluna STATUS na saída do seu terminal
```

Acesse o Airflow em **http://localhost:8080** com as credenciais definidas no `.env`.
