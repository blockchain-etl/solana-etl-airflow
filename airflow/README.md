# Solana ETL Airflow

Airflow DAGs for exporting and loading the Solana blockchain data to Google BigQuery:

## Prerequisites

- linux/macos terminal
- git
- docker
- [gcloud](https://cloud.google.com/sdk/install)

## Setting Up

1. Create a GCS bucket to hold export files:

   ```bash
   gcloud config set project <your_gcp_project>
   PROJECT=$(gcloud config get-value project 2> /dev/null)
   ENVIRONMENT_INDEX=0
   BUCKET=${PROJECT}-${ENVIRONMENT_INDEX}
   gsutil mb gs://${BUCKET}/
   ```

2. Create a Google Cloud Composer environment:

   ```bash
   ENVIRONMENT_NAME=${PROJECT}-${ENVIRONMENT_INDEX} && echo "Environment name is ${ENVIRONMENT_NAME}"
   gcloud composer environments create ${ENVIRONMENT_NAME} --location=us-central1 --zone=us-central1-a \
       --disk-size=30GB --machine-type=n1-standard-1 --node-count=3 --python-version=3 --image-version=composer-2-airflow-2 \
       --network=default --subnetwork=default

   gcloud composer environments update $ENVIRONMENT_NAME --location=us-central1 --update-pypi-packages-from-file=requirements.txt
   ```

   Note that if Composer API is not enabled the command above will auto prompt to enable it.

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
