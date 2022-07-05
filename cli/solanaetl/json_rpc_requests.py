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


def generate_get_block_by_number_json_rpc(block_numbers, include_transactions: bool, encoding='jsonParsed'):
    for idx, block_number in enumerate(block_numbers):
        yield generate_json_rpc(
            method='getBlock',
            params=[block_number, {
                'encoding': encoding,
                'transactionDetails': 'full' if include_transactions else 'signatures',
                'rewards': True
            }],
            request_id=idx
        )


def generate_get_transaction_json_rpc(tranaction_signatures, encoding='jsonParsed'):
    for idx, tranaction_signature in enumerate(tranaction_signatures):
        yield generate_json_rpc(
            method='getTransaction',
            params=[tranaction_signature, encoding],
            request_id=idx
        )


def generate_get_multiple_accounts_json_rpc(accounts, encoding='jsonParsed'):
    for idx, account in enumerate(accounts):
        yield generate_json_rpc(
            method='getMultipleAccounts',
            params=[account, {
                'encoding': encoding,
            }],
            request_id=idx
        )


def generate_json_rpc(method, params, request_id=1):
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': request_id,
    }
