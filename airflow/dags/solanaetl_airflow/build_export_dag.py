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


import logging
import os
from datetime import timedelta
from tempfile import TemporaryDirectory

import pendulum
from airflow import DAG, configuration
from airflow.operators.python import PythonOperator
from solanaetl.cli import export_blocks_and_transactions, extract_accounts
from solanaetl.cli.extract_token_transfers import extract_token_transfers
from solanaetl.cli.extract_tokens import extract_tokens

from solanaetl_airflow.utils.error_handling import handle_dag_failure
from solanaetl_airflow.utils.gcs import download_from_gcs, upload_to_gcs


def build_export_dag(
    dag_id,
    provider_uris,
    output_bucket,
    export_start_block,
    export_end_block,
    notification_emails=None,
    export_schedule_interval='0 0 * * *',
    export_max_workers=1,
    export_block_batch_size=1,
    export_batch_size=100,
    export_max_active_runs=None,
    export_retries=5,
    **kwargs
):
    default_dag_args = {
        'depends_on_past': False,
        'start_date': pendulum.today(tz='UTC'),
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': export_retries,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': handle_dag_failure,
    }

    if notification_emails and len(notification_emails) > 0:
        default_dag_args['email'] = [email.strip()
                                     for email in notification_emails.split(',')]

    export_blocks_and_transactions_toggle = True
    extract_accounts_toggle = True
    extract_token_transfers_toggle = True
    extract_tokens_toggle = True

    if export_max_active_runs is None:
        export_max_active_runs = configuration.conf.getint(
            'core', 'max_active_runs_per_dag')

    dag = DAG(
        dag_id,
        schedule_interval=export_schedule_interval,
        default_args=default_dag_args,
        max_active_runs=export_max_active_runs
    )

    from airflow.providers.google.cloud.hooks.gcs import GCSHook
    gcs_hook = GCSHook()

    # Export
    def export_path(directory, start_block, end_block):
        return 'export/{directory}/start_block={start_block}/end_block={end_block}/'.format(
            directory=directory, start_block=start_block, end_block=end_block
        )

    def copy_to_export_path(file_path, export_path):
        logging.info('Calling copy_to_export_path({}, {})'.format(
            file_path, export_path))
        filename = os.path.basename(file_path)

        upload_to_gcs(
            gcs_hook=gcs_hook,
            bucket_name=output_bucket,
            object_name=export_path + filename,
            file_name=file_path)

    def copy_from_export_path(export_path, file_path):
        logging.info('Calling copy_from_export_path({}, {})'.format(
            export_path, file_path))
        filename = os.path.basename(file_path)

        download_from_gcs(
            gcs_hook=gcs_hook,
            bucket=output_bucket,
            object=export_path + filename,
            filename=file_path)

    def export_blocks_and_transactions_command(provider_uri, **kwargs):
        with TemporaryDirectory() as tempdir:
            logging.info('Calling export_blocks_and_transactions({}, {}, {}, {}, {}, ...)'.format(
                export_start_block, export_end_block, export_batch_size, provider_uri, export_max_workers))

            export_blocks_and_transactions.callback(
                start_block=export_start_block,
                end_block=export_end_block,
                batch_size=export_block_batch_size,
                provider_uri=provider_uri,
                max_workers=export_max_workers,
                blocks_output=os.path.join(tempdir, 'blocks.csv'),
                transactions_output=os.path.join(tempdir, 'transactions.csv'),
                instructions_output=os.path.join(tempdir, 'instructions.csv')
            )

            copy_to_export_path(
                os.path.join(tempdir, 'blocks.csv'),
                export_path('blocks', export_start_block, export_end_block)
            )

            copy_to_export_path(
                os.path.join(tempdir, 'transactions.csv'),
                export_path('transactions', export_start_block,
                            export_end_block)
            )

            copy_to_export_path(
                os.path.join(tempdir, 'instructions.csv'),
                export_path('instructions', export_start_block,
                            export_end_block)
            )

    def extract_accounts_command(provider_uri, **kwargs):
        with TemporaryDirectory() as tempdir:
            copy_from_export_path(
                export_path('instructions', export_start_block,
                            export_end_block),
                os.path.join(tempdir, 'instructions.csv')
            )

            logging.info('Calling extract_accounts({}, {}, {}, {}, {}, ...)'.format(
                export_start_block, export_end_block, export_batch_size, provider_uri, export_max_workers))

            extract_accounts.callback(
                instructions=os.path.join(tempdir, 'instructions.csv'),
                batch_size=export_batch_size,
                output=os.path.join(tempdir, 'accounts.csv'),
                max_workers=export_max_workers,
                provider_uri=provider_uri
            )

            copy_to_export_path(
                os.path.join(tempdir, 'accounts.csv'),
                export_path('accounts', export_start_block, export_end_block)
            )

    def extract_token_transfers_command(**kwargs):
        with TemporaryDirectory() as tempdir:
            copy_from_export_path(
                export_path('instructions', export_start_block,
                            export_end_block),
                os.path.join(tempdir, 'instructions.csv')
            )

            logging.info('Calling extract_token_transfers({}, {}, {}, {}, ...)'.format(
                export_start_block, export_end_block, export_batch_size, export_max_workers))

            extract_token_transfers.callback(
                instructions=os.path.join(tempdir, 'instructions.csv'),
                batch_size=export_batch_size,
                output=os.path.join(tempdir, 'token_transfers.csv'),
                max_workers=export_max_workers,
            )

            copy_to_export_path(
                os.path.join(tempdir, 'token_transfers.csv'),
                export_path('token_transfers',
                            export_start_block, export_end_block)
            )

    def extract_tokens_command(provider_uri, **kwargs):
        with TemporaryDirectory() as tempdir:
            copy_from_export_path(
                export_path('accounts', export_start_block,
                            export_end_block),
                os.path.join(tempdir, 'accounts.csv')
            )

            logging.info('Calling extract_tokens({}, {}, {}, {}, {}, ...)'.format(
                export_start_block, export_end_block, export_batch_size, provider_uri, export_max_workers))

            extract_tokens.callback(
                accounts=os.path.join(tempdir, 'accounts.csv'),
                batch_size=export_batch_size,
                output=os.path.join(tempdir, 'tokens.csv'),
                max_workers=export_max_workers,
                provider_uri=provider_uri
            )

            copy_to_export_path(
                os.path.join(tempdir, 'tokens.csv'),
                export_path('tokens', export_start_block, export_end_block)
            )

    def add_task(toggle, task_id, python_callable, dependencies=None):
        if toggle:
            operator = PythonOperator(
                task_id=task_id,
                python_callable=python_callable,
                execution_timeout=timedelta(hours=24),
                dag=dag,
            )
            if dependencies is not None and len(dependencies) > 0:
                for dependency in dependencies:
                    if dependency is not None:
                        dependency >> operator
            return operator
        else:
            return None

    # Operators

    export_blocks_and_transactions_operator = add_task(
        export_blocks_and_transactions_toggle,
        'export_blocks_and_transactions',
        add_provider_uri_fallback_loop(
            export_blocks_and_transactions_command, provider_uris),
    )

    extract_accounts_operator = add_task(
        extract_accounts_toggle,
        'extract_accounts',
        add_provider_uri_fallback_loop(
            extract_accounts_command, provider_uris),
        dependencies=[export_blocks_and_transactions_operator]
    )

    extract_token_transfers_operator = add_task(
        extract_token_transfers_toggle,
        'extract_token_transfers',
        extract_token_transfers_command,
        dependencies=[export_blocks_and_transactions_operator]
    )

    extract_tokens_operator = add_task(
        extract_tokens_toggle,
        'extract_tokens',
        add_provider_uri_fallback_loop(
            extract_tokens_command, provider_uris),
        dependencies=[extract_accounts_operator]
    )

    return dag


def add_provider_uri_fallback_loop(python_callable, provider_uris):
    """Tries each provider uri in provider_uris until the command succeeds"""

    def python_callable_with_fallback(**kwargs):
        for index, provider_uri in enumerate(provider_uris):
            kwargs['provider_uri'] = provider_uri
            try:
                python_callable(**kwargs)
                break
            except Exception as e:
                if index < (len(provider_uris) - 1):
                    logging.exception(
                        'An exception occurred. Trying another uri')
                else:
                    raise e

    return python_callable_with_fallback
