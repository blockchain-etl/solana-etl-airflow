# Solana ETL

## Overview

Solana ETL allows you to setup an ETL pipeline in Google Cloud Platform for ingesting Solana blockchain data
into BigQuery. It comes with [CLI tools](/cli) for exporting Solana data into convenient formats like CSVs and relational databases.

## Code quality

Over time, we intend to format python files in this repo using isort and autopep8.
At the moment, we are *only formatting any changed or added files*

We have not implemented any sort of automation (e.g. pre-commit), but a requirements_dev.txt is provided for contributors to use.

## Testing

Various tests are implemented (`airflow/tests`, `cli/tests` and `./tests`).
As part of an effort towards consistency, they all source the same requirements_test.txt.
