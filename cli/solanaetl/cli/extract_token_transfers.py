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

import csv
import json

import click
from blockchainetl_common.file_utils import smart_open
from solanaetl.jobs.exporters.token_transfers_item_exporter import \
    token_transfers_item_exporter
from solanaetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from solanaetl.providers.auto import get_provider_from_uri
from solanaetl.thread_local_proxy import ThreadLocalProxy


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-i', '--instructions', type=str, required=True, help='The CSV file containing transaction instructions.')
@click.option('-b', '--batch-size', default=100, show_default=True, type=int, help='The number of blocks to filter at a time.')
@click.option('-o', '--output', default='-', show_default=True, type=str, help='The output file. If not specified stdout is used.')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The maximum number of workers.')
@click.option('-p', '--provider-uri', default='https://solana-api.projectserum.com', show_default=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'https://solana-api.projectserum.com')
def extract_token_transfers(instructions, batch_size, output, max_workers, provider_uri):
    """Extracts Token transfers from instructions file."""
    with smart_open(instructions, 'r') as instructions_file:
        if instructions.endswith('.json'):
            instructions_reader = (json.loads(line)
                                   for line in instructions_file)
        else:
            instructions_reader = csv.DictReader(instructions_file)

        job = ExtractTokenTransfersJob(
            batch_web3_provider=ThreadLocalProxy(
                lambda: get_provider_from_uri(provider_uri, batch=True)),
            instructions_iterable=instructions_reader,
            batch_size=batch_size,
            max_workers=max_workers,
            item_exporter=token_transfers_item_exporter(output))

        job.run()
