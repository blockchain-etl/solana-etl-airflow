import logging

from blockchainetl_common.jobs.exporters.console_item_exporter import ConsoleItemExporter
from blockchainetl_common.jobs.exporters.in_memory_item_exporter import InMemoryItemExporter
from solanaetl.enumeration.entity_type import EntityType
from solanaetl.jobs.export_blocks_job import ExportBlocksJob
from solanaetl.jobs.extract_accounts_job import ExtractAccountsJob
from solanaetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from solanaetl.jobs.extract_tokens_job import ExtractTokensJob

from solanaetl.streaming.eth_item_id_calculator import SolanaItemIdCalculator
from solanaetl.json_rpc_requests import generate_get_latest_block_json_rpc
import json

class SolanaStreamerAdapter:
    def __init__(
            self,
            batch_web3_provider,
            item_exporter=ConsoleItemExporter(),
            batch_size=100,
            max_workers=5,
            entity_types=tuple(EntityType.ALL_FOR_STREAMING)):
        self.batch_web3_provider = batch_web3_provider
        self.item_exporter = item_exporter
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.entity_types = entity_types
        self.item_id_calculator = SolanaItemIdCalculator()

    def open(self):
        self.item_exporter.open()

    def get_current_block_number(self): 
        blocks_rpc = generate_get_latest_block_json_rpc()
        response = self.batch_web3_provider.make_batch_request(json.dumps(blocks_rpc))
        return response['result']

    def export_all(self, start_block, end_block):
        # Export blocks, transactions and instructions
        blocks, transactions, instructions = [], [], []
        if self._should_export(EntityType.BLOCK) or self._should_export(EntityType.TRANSACTION) or self._should_export(EntityType.INSTRUCTION):
            blocks, transactions, instructions = self._export_blocks_transactions_instructions(start_block, end_block)

        # Export receipts and logs
        accounts = []
        if self._should_export(EntityType.ACCOUNT):
            accounts = self._export_accounts(instructions)

        # Extract token transfers
        token_transfers = []
        if self._should_export(EntityType.TOKEN_TRANSFER):
            token_transfers = self._extract_token_transfers(instructions)

        # Export tokens
        tokens = []
        if self._should_export(EntityType.TOKEN):
            tokens = self._extract_tokens(accounts)

        logging.info('Exporting with ' + type(self.item_exporter).__name__)

        all_items = \
           blocks + \
           transactions + \
            instructions + \
            token_transfers + \
            accounts + \
            tokens

        self.calculate_item_ids(all_items)

        self.item_exporter.export_items(all_items)

    def _export_blocks_transactions_instructions(self, start_block, end_block):
        blocks_transactions_instructions_item_exporter = InMemoryItemExporter(item_types=['block', 'transaction', 'instruction'])
        blocks_and_transactions_job = ExportBlocksJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=blocks_transactions_instructions_item_exporter,
            export_blocks=self._should_export(EntityType.BLOCK),
            export_transactions=self._should_export(EntityType.TRANSACTION),
            export_instructions=self._should_export(EntityType.INSTRUCTION)
        )
        blocks_and_transactions_job.run()
        blocks = blocks_transactions_instructions_item_exporter.get_items('block')
        transactions = blocks_transactions_instructions_item_exporter.get_items('transaction')
        instructions = blocks_transactions_instructions_item_exporter.get_items('instruction')

        return blocks, transactions, instructions 

    def _export_accounts(self, instructions):
        exporter = InMemoryItemExporter(item_types=['account'])
        job = ExtractAccountsJob(
            instructions_iterable=instructions,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=exporter,
        )
        job.run()
        accounts = exporter.get_items('account')
        return accounts

    def _extract_token_transfers(self, instructions):
        exporter = InMemoryItemExporter(item_types=['token_transfer'])
        job = ExtractTokenTransfersJob(
            instructions_iterable=instructions,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter)
        job.run()
        token_transfers = exporter.get_items('token_transfer')
        return token_transfers

    def _extract_tokens(self, accounts):
        exporter = InMemoryItemExporter(item_types=['token'])
        job = ExtractTokensJob(
            accounts_iterable=accounts,
            batch_size=self.batch_size,
            batch_web3_provider= self.batch_web3_provider,           
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        tokens = exporter.get_items('token')
        return tokens

    def _should_export(self, entity_type):
        if entity_type == EntityType.BLOCK:
            return True

        if entity_type == EntityType.TRANSACTION:
            return EntityType.TRANSACTION in self.entity_types 

        if entity_type == EntityType.INSTRUCTION:
            return EntityType.INSTRUCTION in self.entity_types or self._should_export(EntityType.ACCOUNT)

        if entity_type == EntityType.ACCOUNT:
            return EntityType.ACCOUNT in self.entity_types or self._should_export(EntityType.TOKEN)

        if entity_type == EntityType.TOKEN_TRANSFER:
            return EntityType.TOKEN_TRANSFER in self.entity_types

        if entity_type == EntityType.TOKEN:
            return EntityType.TOKEN in self.entity_types

        raise ValueError('Unexpected entity type ' + entity_type)

    def calculate_item_ids(self, items):
        for item in items:
            item['item_id'] = self.item_id_calculator.calculate(item)

    def close(self):
        self.item_exporter.close()

def sort_by(arr, fields):
    if isinstance(fields, tuple):
        fields = tuple(fields)
    return sorted(arr, key=lambda item: tuple(item.get(f) for f in fields))
