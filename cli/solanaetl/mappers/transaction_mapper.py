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


from solanaetl.domain.block import Block
from solanaetl.domain.transaction import Transaction


class TransactionMapper(object):
    def json_dict_to_transaction(self, json_dict, **kwargs):
        transaction = Transaction()

        transaction.block_hash = kwargs.get('block_hash')
        transaction.block_number = kwargs.get('block_number')
        transaction.block_timestamp = kwargs.get('block_timestamp')

        tx_json = json_dict.get('transaction')
        if tx_json is not None:
            transaction.signature = tx_json.get('signatures')[0]
            transaction.signer = tx_json.get('message').get('accountKeys')[0]
            transaction.previous_block_hash = tx_json.get(
                'message').get('recentBlockhash')

        tx_meta_json = json_dict.get('meta')
        if tx_meta_json is not None:
            transaction.fee = tx_meta_json.get('fee')

        return transaction

    def transaction_to_dict(self, transaction: Transaction):
        return {
            'type': 'transaction',
            'signature': transaction.signature,
            'signer': transaction.signer,
            'block_hash': transaction.block_hash,
            'previous_block_hash': transaction.previous_block_hash,
            'block_number': transaction.block_number,
            'block_timestamp': transaction.block_timestamp,
            'fee': transaction.fee,
        }
