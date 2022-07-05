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
from solanaetl.domain.block import Block
from solanaetl.executors.batch_work_executor import BatchWorkExecutor
from solanaetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from solanaetl.mappers.block_mapper import BlockMapper
from solanaetl.mappers.transaction_mapper import TransactionMapper
from solanaetl.providers.batch import BatchProvider
from solanaetl.utils import rpc_response_batch_to_results, validate_range


class ExportBlocksJob(BaseJob):
    def __init__(self,
                 start_block,
                 end_block,
                 batch_size,
                 batch_web3_provider: BatchProvider,
                 max_workers,
                 item_exporter: CompositeItemExporter,
                 export_blocks=True,
                 export_transactions=True) -> None:
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block

        self.batch_web3_provider = batch_web3_provider

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.export_blocks = export_blocks
        self.export_transactions = export_transactions
        if not self.export_blocks and not self.export_transactions:
            raise ValueError(
                'At least one of export_blocks or export_transactions must be True')

        self.block_mapper = BlockMapper()
        self.transaction_mapper = TransactionMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch: List[int]):
        blocks_rpc = list(generate_get_block_by_number_json_rpc(
            block_number_batch, self.export_transactions))
        response = [self.batch_web3_provider.make_batch_request(
            json.dumps(block_rpc)) for block_rpc in blocks_rpc]
        results = rpc_response_batch_to_results(response)
        blocks = [self.block_mapper.json_dict_to_block(
            result) for result in results]

        for block in blocks:
            self._export_block(block)

    def _export_block(self, block: Block):
        if self.export_blocks:
            self.item_exporter.export_item(
                self.block_mapper.block_to_dict(block))
        if self.export_transactions:
            for tx in block.transactions:
                self.item_exporter.export_item(
                    self.transaction_mapper.transaction_to_dict(tx))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
