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

import click
from blockchainetl_common.logging_utils import logging_basic_config
from solanaetl.jobs.export_all_common import export_all_common

logging_basic_config()


def is_block_range(start, end):
    """Checks for a valid block number."""
    return (start.isdigit() and 0 <= int(start) <= 9999999999999999 and
            end.isdigit() and 0 <= int(end) <= 9999999999999999)


def get_partitions(start, end, partition_batch_size):
    """Yield partitions based on input data type."""
    if is_block_range(start, end):
        start_block = int(start)
        end_block = int(end)

        for batch_start_block in range(start_block, end_block + 1, partition_batch_size):
            batch_end_block = batch_start_block + partition_batch_size - 1
            if batch_end_block > end_block:
                batch_end_block = end_block

            padded_batch_start_block = str(batch_start_block).zfill(16)
            padded_batch_end_block = str(batch_end_block).zfill(16)
            partition_dir = '/start_block={padded_batch_start_block}/end_block={padded_batch_end_block}'.format(
                padded_batch_start_block=padded_batch_start_block,
                padded_batch_end_block=padded_batch_end_block,
            )
            yield batch_start_block, batch_end_block, partition_dir

    else:
        raise ValueError(
            'start and end must be either block numbers')


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start', required=True, type=str, help='Start block/ISO date/Unix time')
@click.option('-e', '--end', required=True, type=str, help='End block/ISO date/Unix time')
@click.option('-b', '--partition-batch-size', default=10000, show_default=True, type=int,
              help='The number of blocks to export in partition.')
@click.option('-p', '--provider-uri', default='https://api.mainnet-beta.solana.com', show_default=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'https://api.mainnet-beta.solana.com')
@click.option('-o', '--output-dir', default='output', show_default=True, type=str, help='Output directory, partitioned in Hive style.')
@click.option('-w', '--max-workers', default=1, show_default=True, type=int, help='The maximum number of workers.')
@click.option('-B', '--export-batch-size', default=100, show_default=True, type=int, help='The number of requests in JSON RPC batches.')
def export_all(start, end, partition_batch_size, provider_uri, output_dir, max_workers, export_batch_size):
    """Exports all data for a range of blocks."""
    export_all_common(get_partitions(start, end, partition_batch_size),
                      output_dir, provider_uri, max_workers, export_batch_size)
