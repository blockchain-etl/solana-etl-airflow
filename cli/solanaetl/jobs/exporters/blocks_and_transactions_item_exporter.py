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

from blockchainetl_common.jobs.exporters.composite_item_exporter import \
    CompositeItemExporter
from solanaetl.jobs.exporters.instructions_item_exporter import \
    INSTRUCTION_FIELDS_TO_EXPORT

BLOCK_FIELDS_TO_EXPORT = [
    'number',
    'height',
    'hash',
    'previous_block_hash',
    'timestamp',
    'transaction_count',
    'rewards',
    'leader_reward',
    'leader',
]

TRANSACTION_FIELDS_TO_EXPORT = [
    'signature',
    'block_hash',
    'previous_block_hash',
    'block_number',
    'block_timestamp',
    'fee',
    'status',
    'err',
    'accounts',
    'log_messages',
    'balance_changes',
    'pre_token_balances',
    'post_token_balances',
]


def blocks_and_transactions_item_exporter(blocks_output=None, transactions_output=None, instructions_output=None):
    return CompositeItemExporter(
        filename_mapping={
            'block': blocks_output,
            'transaction': transactions_output,
            'instruction': instructions_output,
        },
        field_mapping={
            'block': BLOCK_FIELDS_TO_EXPORT,
            'transaction': TRANSACTION_FIELDS_TO_EXPORT,
            'instruction': INSTRUCTION_FIELDS_TO_EXPORT,
        }
    )
