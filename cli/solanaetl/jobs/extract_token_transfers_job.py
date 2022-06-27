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


from blockchainetl_common.jobs.base_job import BaseJob
from blockchainetl_common.jobs.exporters.composite_item_exporter import \
    CompositeItemExporter
from solanaetl.executors.batch_work_executor import BatchWorkExecutor
from solanaetl.mappers.instruction_mapper import InstructionMapper
from solanaetl.mappers.token_transfer_mapper import TokenTransferMapper
from solanaetl.providers.batch import BatchProvider
from solanaetl.services.token_transfer_extractor import TokenTransferExtractor


class ExportTokenTransfersJob(BaseJob):
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
        self.token_transfer_mapper = TokenTransferMapper()
        self.token_transfer_extractor = TokenTransferExtractor()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            self.instructions_iterable, self._extract_transfers)

    def _extract_transfers(self, instruction_dicts):
        for instruction_dict in instruction_dicts:
            self._extract_transfer(instruction_dict)

    def _extract_transfer(self, instruction_dict):
        instruction = self.instruction_mapper.dict_to_instruction(
            instruction_dict)
        token_transfer = self.token_transfer_extractor.extract_transfer_from_instruction(
            instruction)
        if token_transfer is not None:
            self.item_exporter.export_item(
                self.token_transfer_mapper.token_transfer_to_dict(token_transfer))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
