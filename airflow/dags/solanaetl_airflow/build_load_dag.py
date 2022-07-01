# The MIT License (MIT)
# Copyright (c) 2022 Gamejam.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import json
import os
from datetime import timedelta
from tempfile import TemporaryDirectory

import pendulum
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import \
    GCSToBigQueryOperator
from google.cloud import bigquery

from solanaetl_airflow.utils.error_handling import handle_dag_failure
from solanaetl_airflow.utils.gcs import upload_to_gcs


def build_load_dag(
    dag_id,
    output_bucket,
    checkpoint_bucket,
    destination_dataset_project_id,
    load_start_block,
    load_end_block,
    chain='solana',
    notification_emails=None,
    load_schedule_interval='0 0 * * *',
    load_all_partitions=True
):
    # The following datasets must be created in BigQuery:
    # - crypto_{chain}_raw
    # - crypto_{chain}_temp
    # - crypto_{chain}

    dataset_name = f'crypto_{chain}'
    dataset_name_raw = f'crypto_{chain}_raw'
    dataset_name_temp = f'crypto_{chain}_temp'

    if not destination_dataset_project_id:
        raise ValueError('destination_dataset_project_id is required')

    environment = {
        'dataset_name': dataset_name,
        'dataset_name_raw': dataset_name_raw,
        'dataset_name_temp': dataset_name_temp,
        'destination_dataset_project_id': destination_dataset_project_id,
        'load_all_partitions': load_all_partitions
    }

    def read_file(file_path):
        with open(file_path) as f:
            content = f.read()
            return content

    default_dag_args = {
        'depends_on_past': False,
        'start_date': pendulum.today(tz='UTC'),
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 5,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': handle_dag_failure,
    }

    if notification_emails and len(notification_emails) > 0:
        default_dag_args['email'] = [email.strip()
                                     for email in notification_emails.split(',')]

    # Define a DAG (directed acyclic graph) of tasks.
    dag = DAG(
        dag_id,
        catchup=False,
        schedule_interval=load_schedule_interval,
        default_args=default_dag_args)

    dags_folder = os.environ.get('DAGS_FOLDER', '/opt/airflow/dags')

    from airflow.providers.google.cloud.hooks.gcs import GCSHook
    gcs_hook = GCSHook()

    def add_load_tasks(task, file_format, allow_quoted_newlines=False):
        wait_sensor = GCSObjectExistenceSensor(
            task_id=f'wait_latest_{task}',
            timeout=12 * 60 * 60,
            poke_interval=60,
            bucket=output_bucket,
            object=f'export/{task}/start_block={load_start_block}/end_block={load_end_block}/{task}.{file_format}',
            dag=dag
        )

        schema_path = os.path.join(
            dags_folder, f'resources/stages/raw/schemas/{task}.json')

        load_operator = GCSToBigQueryOperator(
            task_id=f'load_{task}',
            execution_timeout=timedelta(minutes=30),
            dag=dag,
            bucket=output_bucket,
            source_objects=f'export/{task}/*.{file_format}',
            destination_project_dataset_table=f'{destination_dataset_project_id}.{dataset_name_raw}.{task}',
            schema_fields=json.loads(read_file((schema_path))),
            source_format=bigquery.SourceFormat.CSV if file_format == 'csv' else bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            skip_leading_rows=1 if file_format == 'csv' else 0,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            allow_quoted_newlines=allow_quoted_newlines,
            ignore_unknown_values=True,
        )

        wait_sensor >> load_operator
        return load_operator

    def add_save_checkpoint_tasks(dependencies=None):
        def save_checkpoint(**kwargs):
            with TemporaryDirectory() as tempdir:
                local_path = os.path.join(tempdir, "checkpoint.txt")
                remote_path = f'load/checkpoint/start_block={load_start_block}/end_block={load_end_block}/checkpoint.txt'
                open(local_path, mode='a').close()
                upload_to_gcs(
                    gcs_hook=gcs_hook,
                    bucket=checkpoint_bucket,
                    object=remote_path,
                    filename=local_path)

        save_checkpoint_task = PythonOperator(
            task_id='save_checkpoint',
            python_callable=save_checkpoint,
            provide_context=True,
            execution_timeout=timedelta(hours=1),
            dag=dag,
        )
        if dependencies is not None and len(dependencies) > 0:
            for dependency in dependencies:
                dependency >> save_checkpoint_task
        return save_checkpoint_task

    load_blocks_task = add_load_tasks('blocks', 'csv')
    load_transactions_task = add_load_tasks('transactions', 'csv')
    load_instructions_task = add_load_tasks('instructions', 'csv')

    return dag
