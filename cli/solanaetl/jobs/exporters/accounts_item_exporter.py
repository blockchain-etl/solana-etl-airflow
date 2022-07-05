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

ACCOUNT_FIELDS_TO_EXPORT = [
    'pubkey',
    'tx_signature',
    'executable',
    'lamports',
    'owner',
    'rent_epoch',
    'program',
    'space',
    'account_type',
    'is_native',
    'mint',
    'state',
    'token_amount',
    'token_amount_decimals',
    'program_data',
    'authorized_voters',
    'authorized_withdrawer',
    'prior_voters',
    'node_pubkey',
    'commission',
    'epoch_credits',
    'votes',
    'root_slot',
    'last_timestamp',
    'data',
]


def accounts_item_exporter(accounts_output=None):
    return CompositeItemExporter(
        filename_mapping={
            'account': accounts_output,
        },
        field_mapping={
            'account': ACCOUNT_FIELDS_TO_EXPORT,
        }
    )
