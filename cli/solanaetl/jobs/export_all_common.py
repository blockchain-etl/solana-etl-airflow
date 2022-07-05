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
import shutil
from time import time

from solanaetl.jobs.export_blocks_job import ExportBlocksJob
from solanaetl.jobs.exporters.accounts_item_exporter import \
    accounts_item_exporter
from solanaetl.jobs.exporters.blocks_and_transactions_item_exporter import \
    blocks_and_transactions_item_exporter
from solanaetl.jobs.exporters.tokens_item_exporter import tokens_item_exporter
from solanaetl.jobs.exporters.token_transfers_item_exporter import \
    token_transfers_item_exporter
from solanaetl.jobs.extract_accounts_job import ExtractAccountsJob
from solanaetl.jobs.extract_tokens_job import ExtractTokensJob
from solanaetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from solanaetl.providers.auto import get_provider_from_uri
from solanaetl.thread_local_proxy import ThreadLocalProxy
from solanaetl.utils import get_item_iterable

logger = logging.getLogger('export_all')


def export_all_common(partitions, output_dir, provider_uri, max_workers, batch_size):
    for batch_start_block, batch_end_block, partition_dir in partitions:
        # # # start # # #

        start_time = time()

        padded_batch_start_block = str(batch_start_block).zfill(8)
        padded_batch_end_block = str(batch_end_block).zfill(8)
        block_range = '{padded_batch_start_block}-{padded_batch_end_block}'.format(
            padded_batch_start_block=padded_batch_start_block,
            padded_batch_end_block=padded_batch_end_block,
        )
        file_name_suffix = '{padded_batch_start_block}_{padded_batch_end_block}'.format(
            padded_batch_start_block=padded_batch_start_block,
            padded_batch_end_block=padded_batch_end_block,
        )

        cache_output_dir = '{output_dir}/.tmp{partition_dir}'.format(
            output_dir=output_dir,
            partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(cache_output_dir), exist_ok=True)

        # # # blocks_and_transactions # # #

        blocks_output_dir = '{output_dir}/blocks{partition_dir}'.format(
            output_dir=output_dir,
            partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(blocks_output_dir), exist_ok=True)

        transactions_output_dir = '{output_dir}/transactions{partition_dir}'.format(
            output_dir=output_dir,
            partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(transactions_output_dir), exist_ok=True)

        instructions_output_dir = '{output_dir}/instructions{partition_dir}'.format(
            output_dir=output_dir,
            partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(transactions_output_dir), exist_ok=True)

        blocks_file = '{blocks_output_dir}/blocks_{file_name_suffix}.csv'.format(
            blocks_output_dir=blocks_output_dir,
            file_name_suffix=file_name_suffix,
        )
        transactions_file = '{transactions_output_dir}/transactions_{file_name_suffix}.csv'.format(
            transactions_output_dir=transactions_output_dir,
            file_name_suffix=file_name_suffix,
        )
        instructions_file = '{instructions_output_dir}/instructions_{file_name_suffix}.csv'.format(
            instructions_output_dir=instructions_output_dir,
            file_name_suffix=file_name_suffix,
        )
        logger.info('Exporting blocks {block_range} to {blocks_file}'.format(
            block_range=block_range,
            blocks_file=blocks_file,
        ))
        logger.info('Exporting transactions from blocks {block_range} to {transactions_file}'.format(
            block_range=block_range,
            transactions_file=transactions_file,
        ))
        logger.info('Exporting instructions from blocks {block_range} to {instructions_file}'.format(
            block_range=block_range,
            instructions_file=instructions_file,
        ))

        job = ExportBlocksJob(
            start_block=batch_start_block,
            end_block=batch_end_block,
            batch_size=batch_size,
            batch_web3_provider=ThreadLocalProxy(
                lambda: get_provider_from_uri(provider_uri, batch=True)),
            max_workers=max_workers,
            item_exporter=blocks_and_transactions_item_exporter(
                blocks_file, transactions_file, instructions_file),
            export_blocks=blocks_file is not None,
            export_transactions=transactions_file is not None,
            export_instructions=instructions_file is not None)

        job.run()

        # # # accounts # # #
        accounts_output_dir = '{output_dir}/accounts{partition_dir}'.format(
            output_dir=output_dir,
            partition_dir=partition_dir
        )
        os.makedirs(os.path.dirname(accounts_output_dir), exist_ok=True)

        accounts_file = '{accounts_output_dir}/accounts_{file_name_suffix}.csv'.format(
            accounts_output_dir=accounts_output_dir,
            file_name_suffix=file_name_suffix,
        )

        logger.info('Extracting accounts from blocks {block_range} to {accounts_file}'.format(
            block_range=block_range,
            accounts_file=accounts_file,
        ))

        with get_item_iterable(instructions_file) as instructions_reader:
            job = ExtractAccountsJob(
                batch_web3_provider=ThreadLocalProxy(
                    lambda: get_provider_from_uri(provider_uri, batch=True)),
                instructions_iterable=instructions_reader,
                batch_size=batch_size,
                max_workers=max_workers,
                item_exporter=accounts_item_exporter(accounts_file))

            job.run()

        # # # token transfers # # #
        token_transfers_output_dir = '{output_dir}/token_transfers{partition_dir}'.format(
            output_dir=output_dir,
            partition_dir=partition_dir
        )
        os.makedirs(os.path.dirname(token_transfers_output_dir), exist_ok=True)

        token_transfers_file = '{token_transfers_output_dir}/token_transfers_{file_name_suffix}.csv'.format(
            token_transfers_output_dir=token_transfers_output_dir,
            file_name_suffix=file_name_suffix,
        )

        logger.info('Extracting token transfers from blocks {block_range} to {token_transfers_file}'.format(
            block_range=block_range,
            token_transfers_file=token_transfers_file,
        ))

        with get_item_iterable(instructions_file) as instructions_reader:
            job = ExtractTokenTransfersJob(
                instructions_iterable=instructions_reader,
                batch_size=batch_size,
                max_workers=max_workers,
                item_exporter=token_transfers_item_exporter(token_transfers_file))

            job.run()

        # # # tokens # # #
        tokens_output_dir = '{output_dir}/tokens{partition_dir}'.format(
            output_dir=output_dir,
            partition_dir=partition_dir
        )
        os.makedirs(os.path.dirname(tokens_output_dir), exist_ok=True)

        tokens_file = '{tokens_output_dir}/tokens_{file_name_suffix}.csv'.format(
            tokens_output_dir=tokens_output_dir,
            file_name_suffix=file_name_suffix,
        )

        logger.info('Extracting tokens from blocks {block_range} to {tokens_file}'.format(
            block_range=block_range,
            tokens_file=tokens_file,
        ))

        with get_item_iterable(accounts_file) as accounts_reader:
            job = ExtractTokensJob(
                batch_web3_provider=ThreadLocalProxy(
                    lambda: get_provider_from_uri(provider_uri, batch=True)),
                accounts_iterable=accounts_reader,
                batch_size=batch_size,
                max_workers=max_workers,
                item_exporter=tokens_item_exporter(tokens_file))

            job.run()

        # # # finish # # #
        shutil.rmtree(os.path.dirname(cache_output_dir))
        end_time = time()
        time_diff = round(end_time - start_time, 5)
        logger.info('Exporting blocks {block_range} took {time_diff} seconds'.format(
            block_range=block_range,
            time_diff=time_diff,
        ))
