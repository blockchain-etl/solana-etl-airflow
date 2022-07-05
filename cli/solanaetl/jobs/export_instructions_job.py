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
from solanaetl.domain.transaction import Transaction
from solanaetl.executors.batch_work_executor import BatchWorkExecutor
from solanaetl.json_rpc_requests import generate_get_transaction_json_rpc
from solanaetl.mappers.instruction_mapper import InstructionMapper
from solanaetl.mappers.transaction_mapper import TransactionMapper
from solanaetl.providers.batch import BatchProvider
from solanaetl.services.instruction_parser import InstructionParser
from solanaetl.utils import rpc_response_batch_to_results


class ExportInstructionsJob(BaseJob):
    def __init__(self,
                 batch_web3_provider: BatchProvider,
                 item_exporter: CompositeItemExporter,
                 transaction_addresses_iterable,
                 max_workers) -> None:
        self.item_exporter = item_exporter
        self.transaction_addresses_iterable = transaction_addresses_iterable
        self.batch_work_executor = BatchWorkExecutor(1, max_workers)
        self.batch_web3_provider = batch_web3_provider

        self.transaction_mapper = TransactionMapper()
        self.instruction_mapper = InstructionMapper()
        self.instruction_parser = InstructionParser()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            self.transaction_addresses_iterable, self._export_instructions)

    def _export_instructions(self, transaction_addresses):
        transactions_rpc = list(
            generate_get_transaction_json_rpc(transaction_addresses))
        response = self.batch_web3_provider.make_batch_request(
            json.dumps(transactions_rpc))
        results = rpc_response_batch_to_results(response)
        transactions = [self.transaction_mapper.from_json_dict(
            result) for result in results]

        for transaction in transactions:
            self._export_instructions_in_transaction(transaction)

    def _export_instructions_in_transaction(self, transaction: Transaction):
        for instruction in transaction.instructions:
            instruction = self.instruction_parser.parse(instruction)
            instruction_dict = self.instruction_mapper.to_dict(
                instruction)
            self.item_exporter.export_item(instruction_dict)

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
