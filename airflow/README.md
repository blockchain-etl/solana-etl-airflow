# Solana ETL Airflow

Airflow DAGs for exporting and loading the Solana blockchain data to Google BigQuery:

## Prerequisites

- linux/macos terminal
- git
- docker
- [gcloud](https://cloud.google.com/sdk/install)

## Run with Docker

Setting the right Airflow user

```shell
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

---

Initialize database

```shell
docker-compose up airflow-init
```

The account created has the login `airflow` and the password `airflow`.

---

Running Airflow

```shell
docker-compose up --build
```

Web UI available on <http://localhost:8080>
