FROM apache/airflow:2.3.2

USER root

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y --no-install-recommends build-essential gcc

USER airflow

# Install required package for local development
RUN pip install --no-cache-dir \
        discord-webhook \
        google-cloud \
        google-api-python-client \
        apache-airflow-providers-google

# Install SolanaETL CLI for local development
COPY --chown=airflow ./cli ./cli
RUN cd ./cli && python setup.py install --user