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
from typing import List

from blockchainetl_common.jobs.base_job import BaseJob
from blockchainetl_common.jobs.exporters.composite_item_exporter import \
    CompositeItemExporter
from solanaetl.domain.account import Account
from solanaetl.executors.batch_work_executor import BatchWorkExecutor
from solanaetl.json_rpc_requests import generate_get_multiple_accounts_json_rpc
from solanaetl.mappers.account_mapper import AccountMapper
from solanaetl.mappers.instruction_mapper import InstructionMapper
from solanaetl.providers.batch import BatchProvider
from solanaetl.services.account_extractor import \
    extract_account_pubkey_from_instruction
from solanaetl.utils import rpc_response_batch_to_results


class ExtractAccountsJob(BaseJob):
    def __init__(
            self,
            batch_web3_provider: BatchProvider,
            instructions_iterable,
            batch_size,
            max_workers,
            item_exporter: CompositeItemExporter):
        self.batch_web3_provider = batch_web3_provider
        self.instructions_iterable = instructions_iterable

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.instruction_mapper = InstructionMapper()
        self.account_mapper = AccountMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        # Only extract created account on block
        created_accounts = [extract_account_pubkey_from_instruction(
            self.instruction_mapper.from_dict(instruction)) for instruction in self.instructions_iterable]
        created_accounts = [
            account for account in created_accounts if account.pubkey is not None]

        self.batch_work_executor.execute(
            created_accounts, self._extract_accounts)

    def _extract_accounts(self, accounts: List[Account]):
        account_keys = [account.pubkey for account in accounts]
        rpc_requests = list(
            generate_get_multiple_accounts_json_rpc([account_keys]))

        response = self.batch_web3_provider.make_batch_request(
            json.dumps(rpc_requests))
        results = rpc_response_batch_to_results(response)

        accounts = [
            self.account_mapper.from_json_dict(
                json_dict,
                pubkey=accounts[idx].pubkey,
                tx_signature=accounts[idx].tx_signature)
            for result in results
            for idx, json_dict in enumerate(result.get('value'))
        ]

        for account in accounts:
            self._extract_account(account)

    def _extract_account(self, account: Account):
        self.item_exporter.export_item(
            self.account_mapper.to_dict(account))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
