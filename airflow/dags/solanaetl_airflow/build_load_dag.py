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
import logging
import os
import time
from datetime import timedelta
from tempfile import TemporaryDirectory

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import \
    GCSToBigQueryOperator
from google.cloud import bigquery
from google.cloud.bigquery import TimePartitioning
from airflow.operators.email import EmailOperator

from solanaetl_airflow.utils.bigquery import submit_bigquery_job
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

    def add_enrich_tasks(task, time_partitioning_field='block_timestamp', dependencies=None, always_load_all_partitions=False):
        """
        block_timestamp can be null, should not require to use Partition filter. Ex: block 1
        """
        def enrich_task(ds, **kwargs):
            template_context = kwargs.copy()
            template_context['ds'] = ds
            template_context['params'] = environment

            bq_hook = BigQueryHook()
            bq_client = bq_hook.get_client()

            # Need to use a temporary table because bq query sets field modes to NULLABLE and descriptions to null
            # when writeDisposition is WRITE_TRUNCATE

            # Create a temporary table
            temp_table_name = f'{task}_{int(round(time.time() * 1000))}'
            temp_table_ref = bq_client.dataset(
                dataset_name_temp).table(temp_table_name)

            schema_path = os.path.join(
                dags_folder, f'resources/stages/enrich/schemas/{task}.json')
            # schema = read_bigquery_schema_from_file(schema_path)
            table = bigquery.Table(
                temp_table_ref, schema=json.loads(read_file((schema_path))))

            description_path = os.path.join(
                dags_folder, f'resources/stages/enrich/descriptions/{task}.txt')
            table.description = read_file(description_path)
            if time_partitioning_field is not None:
                table.time_partitioning = TimePartitioning(
                    field=time_partitioning_field)
            logging.info('Creating table: ' + json.dumps(table.to_api_repr()))
            table = bq_client.create_table(table)
            assert table.table_id == temp_table_name

            # Query from raw to temporary table
            query_job_config = bigquery.QueryJobConfig()
            # Finishes faster, query limit for concurrent interactive queries is 50
            query_job_config.priority = bigquery.QueryPriority.INTERACTIVE
            query_job_config.destination = temp_table_ref

            sql_path = os.path.join(
                dags_folder, 'resources/stages/enrich/sqls/{task}.sql'.format(task=task))
            sql_template = read_file(sql_path)
            sql = kwargs['task'].render_template(
                sql_template, template_context)
            print('Enrichment sql:')
            print(sql)

            query_job = bq_client.query(
                sql, location='US', job_config=query_job_config)
            submit_bigquery_job(query_job, query_job_config)
            assert query_job.state == 'DONE'

            if load_all_partitions or always_load_all_partitions:
                # Copy temporary table to destination
                copy_job_config = bigquery.CopyJobConfig()
                copy_job_config.write_disposition = 'WRITE_TRUNCATE'
                dest_table_name = f'{task}'
                dest_table_ref = bq_client.dataset(
                    dataset_name, project=destination_dataset_project_id).table(dest_table_name)
                copy_job = bq_client.copy_table(
                    temp_table_ref, dest_table_ref, location='US', job_config=copy_job_config)
                submit_bigquery_job(copy_job, copy_job_config)
                assert copy_job.state == 'DONE'
            else:
                # Merge
                # https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax#merge_statement
                merge_job_config = bigquery.QueryJobConfig()
                # Finishes faster, query limit for concurrent interactive queries is 50
                merge_job_config.priority = bigquery.QueryPriority.INTERACTIVE

                merge_sql_path = os.path.join(
                    dags_folder, f'resources/stages/enrich/sqls/merge/merge_{task}.sql')
                merge_sql_template = read_file(merge_sql_path)

                merge_template_context = template_context.copy()
                merge_template_context['params']['source_table'] = temp_table_name
                merge_template_context['params']['destination_dataset_project_id'] = destination_dataset_project_id
                merge_template_context['params']['destination_dataset_name'] = dataset_name
                merge_sql = kwargs['task'].render_template(
                    merge_sql_template, merge_template_context)
                print('Merge sql:')
                print(merge_sql)
                merge_job = bq_client.query(
                    merge_sql, location='US', job_config=merge_job_config)
                submit_bigquery_job(merge_job, merge_job_config)
                assert merge_job.state == 'DONE'

            # Delete temp table
            bq_client.delete_table(temp_table_ref)

        enrich_operator = PythonOperator(
            task_id=f'enrich_{task}',
            python_callable=enrich_task,
            execution_timeout=timedelta(minutes=60),
            dag=dag
        )

        if dependencies is not None and len(dependencies) > 0:
            for dependency in dependencies:
                dependency >> enrich_operator
        return enrich_operator

    def add_save_checkpoint_tasks(dependencies=None):
        def save_checkpoint(**kwargs):
            with TemporaryDirectory() as tempdir:
                local_path = os.path.join(tempdir, "checkpoint.txt")
                remote_path = f'load/checkpoint/start_block={load_start_block}/end_block={load_end_block}/checkpoint.txt'
                open(local_path, mode='a').close()
                upload_to_gcs(
                    gcs_hook=gcs_hook,
                    bucket_name=checkpoint_bucket,
                    object_name=remote_path,
                    file_name=local_path)

        save_checkpoint_task = PythonOperator(
            task_id='save_checkpoint',
            python_callable=save_checkpoint,
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
    load_tokens_task = add_load_tasks('tokens', 'csv')
    load_token_transfers_task = add_load_tasks('token_transfers', 'csv')
    load_accounts_task = add_load_tasks('accounts', 'csv')

    enrich_blocks_task = add_enrich_tasks(
        'blocks', time_partitioning_field='timestamp', dependencies=[load_blocks_task])
    enrich_transactions_task = add_enrich_tasks(
        'transactions', dependencies=[load_transactions_task])
    enrich_instructions_task = add_enrich_tasks(
        'instructions', dependencies=[load_transactions_task, load_instructions_task])
    enrich_token_transfers_task = add_enrich_tasks(
        'token_transfers', dependencies=[load_transactions_task, load_token_transfers_task])
    enrich_accounts_task = add_enrich_tasks(
        'accounts', dependencies=[load_transactions_task, load_accounts_task])
    enrich_tokens_task = add_enrich_tasks(
        'tokens', dependencies=[load_transactions_task, load_tokens_task])

    save_checkpoint_task = add_save_checkpoint_tasks(dependencies=[
        enrich_blocks_task,
        enrich_transactions_task,
        enrich_instructions_task,
        enrich_token_transfers_task,
        enrich_accounts_task,
        enrich_tokens_task
    ])

    # Send email task #
    if notification_emails and len(notification_emails) > 0:
        send_email_task = EmailOperator(
            task_id='send_email',
            to=[email.strip() for email in notification_emails.split(',')],
            subject='Solana ETL Airflow Load DAG Succeeded',
            html_content='Solana ETL Airflow Load DAG Succeeded - {}'.format(
                chain),
            dag=dag
        )
        save_checkpoint_task >> send_email_task

    return dag
