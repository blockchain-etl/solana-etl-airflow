FROM python:3.7
ENV PROJECT_DIR=solana-etl

RUN mkdir /$PROJECT_DIR
WORKDIR /$PROJECT_DIR
COPY . .
RUN pip install --upgrade pip && pip install -e /$PROJECT_DIR

# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ENTRYPOINT ["/tini", "--", "python", "solanaetl"]
