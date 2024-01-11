FROM apache/airflow:2.3.2

USER root

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y --no-install-recommends build-essential gcc

USER airflow

# Install required package for local development
COPY --chown=airflow ./cli ./cli
COPY --chown=airflow ./airflow/requirements_local.txt ./airflow/requirements_local.txt
RUN pip install --no-cache-dir \
        --upgrade pip \
        -r ./airflow/requirements_local.txt \
        -e cli
        