# Solana ETL, Airflow

## Overview

Solana ETL Airflow allows you to setup an ETL pipeline in Google Cloud Platform for ingesting Solana blockchain data
into BigQuery via Airflow. It comes with [CLI tools](/cli) for exporting Solana data into convenient formats like CSVs and relational databases.

## Architecture

1. [Airflow DAGs](https://airflow.apache.org/) export and load Solana data to BigQuery daily.
   Refer to [Solana ETL Airflow](/airflow) for deployment instructions.

## Setting Up

1. Follow the instructions in [Solana ETL Airflow](/airflow) to deploy a Cloud Composer cluster for
   exporting and loading historical Solana data. It may take several days for the export DAG to catch up

## Code quality

Over time, we intend to format python files in this repo using isort and autopep8.
At the moment, we are *only formatting any changed or added files*

We have not implemented any sort of automation (e.g. pre-commit), but a requirements_dev.txt is provided for contributors to use.

## Testing

Various tests are implemented (`airflow/tests`, `cli/tests` and `./tests`).
As part of an effort towards consistency, they all source the same requirements_test.txt.
