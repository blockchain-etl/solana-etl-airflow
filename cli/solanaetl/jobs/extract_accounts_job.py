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


import json

from blockchainetl_common.jobs.base_job import BaseJob
from blockchainetl_common.jobs.exporters.composite_item_exporter import \
    CompositeItemExporter
from solanaetl.domain.account import Account
from solanaetl.executors.batch_work_executor import BatchWorkExecutor
from solanaetl.json_rpc_requests import generate_get_multiple_accounts_json_rpc
from solanaetl.mappers.account_mapper import AccountMapper
from solanaetl.mappers.transaction_mapper import TransactionMapper
from solanaetl.providers.batch import BatchProvider
from solanaetl.utils import rpc_response_batch_to_results


class ExtractAccountsJob(BaseJob):
    def __init__(
            self,
            batch_web3_provider: BatchProvider,
            transactions_iterable,
            batch_size,
            max_workers,
            item_exporter: CompositeItemExporter):
        self.batch_web3_provider = batch_web3_provider
        self.transactions_iterable = transactions_iterable

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.transaction_mapper = TransactionMapper()
        self.account_mapper = AccountMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        accountKeys = set({})
        for transaction_dict in self.transactions_iterable:
            transaction = self.transaction_mapper.dict_to_transaction(
                transaction_dict)
            accountKeys = accountKeys.union(set([account.get('pubkey')
                                                for account in transaction.accounts]))

        accountKeys = list(accountKeys)
        self.batch_work_executor.execute(accountKeys, self._extract_accounts)

    def _extract_accounts(self, accountKeys: list):
        rpc_requests = list(
            generate_get_multiple_accounts_json_rpc([accountKeys]))

        response = self.batch_web3_provider.make_batch_request(
            json.dumps(rpc_requests))
        results = rpc_response_batch_to_results(response)

        accounts = [
            self.account_mapper.json_dict_to_account(
                json_dict, accountKey=accountKeys[idx])
            for result in results
            for idx, json_dict in enumerate(result.get('value'))
            if json_dict is not None
        ]

        for account in accounts:
            self._extract_account(account)

    def _extract_account(self, account: Account):
        self.item_exporter.export_item(
            self.account_mapper.account_to_dict(account))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
