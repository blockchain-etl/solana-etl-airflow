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


import base64
import json
from typing import List

from blockchainetl_common.jobs.base_job import BaseJob
from blockchainetl_common.jobs.exporters.composite_item_exporter import \
    CompositeItemExporter
from solanaetl.decoder.metaplex.metadata import (get_metadata_account,
                                                 unpack_metadata_account)
from solanaetl.domain.account import Account
from solanaetl.executors.batch_work_executor import BatchWorkExecutor
from solanaetl.json_rpc_requests import generate_get_multiple_accounts_json_rpc
from solanaetl.mappers.account_mapper import AccountMapper
from solanaetl.mappers.token_mapper import TokenMapper
from solanaetl.providers.batch import BatchProvider
from solanaetl.utils import rpc_response_batch_to_results


class ExtractTokensJob(BaseJob):
    def __init__(
            self,
            batch_web3_provider: BatchProvider,
            accounts_iterable,
            batch_size,
            max_workers,
            item_exporter: CompositeItemExporter):
        self.batch_web3_provider = batch_web3_provider
        self.accounts_iterable = accounts_iterable

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.account_mapper = AccountMapper()
        self.token_mapper = TokenMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        # only extract mint nft on block
        accounts = [
            self.account_mapper.from_dict(account_dict)
            for account_dict in self.accounts_iterable
            if account_dict.get('token_amount_decimals') is not None and account_dict.get('account_type') == 'mint'
        ]

        self.batch_work_executor.execute(
            accounts, self._extract_tokens)

    def _extract_tokens(self, accounts: List[Account]):
        metadata_accounts = [
            str(get_metadata_account(account.pubkey))
            for account in accounts
        ]
        rpc_requests = list(
            generate_get_multiple_accounts_json_rpc([metadata_accounts], encoding='base64'))

        response = self.batch_web3_provider.make_batch_request(
            json.dumps(rpc_requests))
        results = rpc_response_batch_to_results(response)

        tokens = []

        for result in results:
            for idx, value in enumerate(result.get('value')):
                if value is not None:
                    data = base64.b64decode(value.get('data')[0])
                    metadata = unpack_metadata_account(data)
                    tokens.append(
                        self.token_mapper.from_metaplex_metadata(
                            metadata,
                            token_type='nft' if accounts[idx].token_amount_decimals == '0' else 'spl-token',
                            tx_signature=accounts[idx].tx_signature))

        for token in tokens:
            self.item_exporter.export_item(
                self.token_mapper.to_dict(token))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
