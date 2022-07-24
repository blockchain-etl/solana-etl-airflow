# MIT License
#
# Copyright (c) 2022 Tan Sek Fook, sekfook97@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging

import click
from blockchainetl_common.streaming.streaming_utils import configure_signals, configure_logging
from solanaetl.enumeration.entity_type import EntityType

from solanaetl.providers.auto import get_provider_from_uri
from solanaetl.streaming.item_exporter_creator import create_item_exporters
from solanaetl.thread_local_proxy import ThreadLocalProxy


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-l', '--last-synced-block-file', default='last_synced_block.txt', show_default=True, type=str, help='')
@click.option('--lag', default=0, show_default=True, type=int, help='The number of blocks to lag behind the network.')
@click.option('-p', '--provider-uri', default='https://api.mainnet-beta.solana.com', show_default=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'https://api.mainnet-beta.solana.com')
@click.option('-o', '--output', type=str,
              help='Either Google PubSub topic path e.g. projects/your-project/topics/crypto_ethereum; '
                   'or GCS bucket e.g. gs://your-bucket-name; '
                   'If not specified will print to console')
@click.option('-s', '--start-block', default=None, show_default=True, type=int, help='Start block')
@click.option('-e', '--entity-types', default=','.join(EntityType.ALL_FOR_STREAMING), show_default=True, type=str,
              help='The list of entity types to export.')
@click.option('--period-seconds', default=10, show_default=True, type=int, help='How many seconds to sleep between syncs')
@click.option('-b', '--batch-size', default=10, show_default=True, type=int, help='How many blocks to batch in single request')
@click.option('-B', '--block-batch-size', default=1, show_default=True, type=int, help='How many blocks to batch in single sync round')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The number of workers')
@click.option('--log-file', default=None, show_default=True, type=str, help='Log file')
@click.option('--pid-file', default=None, show_default=True, type=str, help='pid file')
def stream(last_synced_block_file, lag, provider_uri, output, start_block, entity_types,
           period_seconds=10, batch_size=2, block_batch_size=10, max_workers=5, log_file=None, pid_file=None):
    """Streams all data types to console or Google Pub/Sub."""
    configure_logging(log_file)
    configure_signals()
    entity_types = parse_entity_types(entity_types)

    from solanaetl.streaming.solana_streamer_adapter import SolanaStreamerAdapter
    from blockchainetl_common.streaming.streamer import Streamer

    logging.info('Using ' + provider_uri)

    streamer_adapter = SolanaStreamerAdapter(
        batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(provider_uri, batch=True)),
        item_exporter=create_item_exporters(output),
        batch_size=batch_size,
        max_workers=max_workers,
        entity_types=entity_types
    )
    streamer = Streamer(
        blockchain_streamer_adapter=streamer_adapter,
        last_synced_block_file=last_synced_block_file,
        lag=lag,
        start_block=start_block,
        period_seconds=period_seconds,
        block_batch_size=block_batch_size,
        pid_file=pid_file
    )
    streamer.stream()


def parse_entity_types(entity_types):
    entity_types = [c.strip() for c in entity_types.split(',')]

    # validate passed types
    for entity_type in entity_types:
        if entity_type not in EntityType.ALL_FOR_STREAMING:
            raise click.BadOptionUsage(
                '--entity-type', '{} is not an available entity type. Supply a comma separated list of types from {}'
                    .format(entity_type, ','.join(EntityType.ALL_FOR_STREAMING)))

    return entity_types
