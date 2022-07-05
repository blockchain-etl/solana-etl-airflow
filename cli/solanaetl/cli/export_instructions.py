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
from blockchainetl_common.file_utils import smart_open
from blockchainetl_common.logging_utils import logging_basic_config
from solanaetl.jobs.export_instructions_job import ExportInstructionsJob
from solanaetl.jobs.exporters.instructions_item_exporter import \
    instructions_item_exporter
from solanaetl.providers.auto import get_provider_from_uri
from solanaetl.thread_local_proxy import ThreadLocalProxy

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-t', '--transaction-addresses', required=True, type=str,
              help='The file containing transaction addresses, one per line.')
@click.option('-o', '--output', default='-', show_default=True, type=str, help='The output file. If not specified stdout is used.')
@click.option('-w', '--max-workers', default=1, show_default=True, type=int, help='The maximum number of workers.')
@click.option('-p', '--provider-uri', default='https://api.mainnet-beta.solana.com', show_default=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'https://api.mainnet-beta.solana.com')
def export_instructions(transaction_addresses, output, max_workers, provider_uri):
    """Exports instructions in transactions."""

    with smart_open(transaction_addresses, 'r') as transaction_addresses_file:
        job = ExportInstructionsJob(
            batch_web3_provider=ThreadLocalProxy(
                lambda: get_provider_from_uri(provider_uri, batch=True)),
            item_exporter=instructions_item_exporter(output),
            max_workers=max_workers,
            transaction_addresses_iterable=(transaction_address.strip(
            ) for transaction_address in transaction_addresses_file),
        )

        job.run()
