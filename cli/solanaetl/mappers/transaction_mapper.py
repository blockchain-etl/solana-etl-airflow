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
from typing import Dict, List

from solanaetl.domain.instruction import Instruction
from solanaetl.domain.transaction import BalanceChange, Transaction
from solanaetl.mappers.account_mapper import AccountMapper
from solanaetl.mappers.instruction_mapper import InstructionMapper


class TransactionMapper(object):
    def __init__(self, instruction_mapper=None, account_mapper=None) -> None:
        self.instruction_mapper = instruction_mapper if instruction_mapper is not None else InstructionMapper()
        self.account_mapper = account_mapper if account_mapper is not None else AccountMapper()

    def from_json_dict(self, json_dict: Dict, **kwargs) -> Transaction:
        transaction = Transaction()

        transaction.block_hash = kwargs.get('block_hash')
        transaction.block_number = kwargs.get('block_number')
        transaction.block_timestamp = kwargs.get('block_timestamp')

        tx_json: Dict = json_dict.get('transaction')
        instructions: List[Instruction] = []
        if tx_json is not None:
            transaction.signature = tx_json.get('signatures')[0]
            transaction.accounts = tx_json.get('message').get('accountKeys')
            transaction.previous_block_hash = tx_json.get(
                'message').get('recentBlockhash')

            if 'instructions' in tx_json.get('message'):
                instructions.extend([
                    self.instruction_mapper.from_json_dict(
                        instruction, tx_signature=transaction.signature, index=index)
                    for index, instruction in enumerate(tx_json.get('message').get('instructions'))
                ])

        # meta
        tx_meta_json: Dict = json_dict.get('meta')
        if tx_meta_json is not None:
            transaction.fee = tx_meta_json.get('fee')
            tx_err = tx_meta_json.get('err')
            transaction.status = "Success" if tx_err is None else "Fail"
            transaction.err = tx_err

            if 'innerInstructions' in tx_meta_json:
                instructions.extend([
                    self.instruction_mapper.from_json_dict(
                        instruction, tx_signature=transaction.signature, index=index, parent_index=inner_instruction.get('index'))
                    for inner_instruction in tx_meta_json.get('innerInstructions')
                    for index, instruction in enumerate(inner_instruction.get('instructions'))
                ])

            if 'logMessages' in tx_meta_json:
                transaction.log_messages = tx_meta_json.get('logMessages')

            balance_changes: List[BalanceChange] = []
            if 'postBalances' in tx_meta_json and 'preBalances' in tx_meta_json:
                post_token_balances = tx_meta_json.get('postBalances')
                pre_token_balances = tx_meta_json.get('preBalances')

                for idx, post_balance in enumerate(post_token_balances):
                    pre_balance = pre_token_balances[idx]
                    account = transaction.accounts[idx]
                    token_balance_change = BalanceChange()
                    token_balance_change.account = account.get('pubkey')
                    token_balance_change.before = pre_balance
                    token_balance_change.after = post_balance
                    balance_changes.append(token_balance_change)

                transaction.balance_changes = balance_changes

            if 'postTokenBalances' in tx_meta_json:
                transaction.post_token_balances = tx_meta_json.get(
                    'postTokenBalances')
            if 'preTokenBalances' in tx_meta_json:
                transaction.pre_token_balances = tx_meta_json.get(
                    'preTokenBalances')

        transaction.instructions = instructions

        return transaction

    def balance_change_to_dict(self, balance_change: BalanceChange):
        return {
            'account': balance_change.account,
            'before': balance_change.before,
            'after': balance_change.after,
        }

    def to_dict(self, transaction: Transaction) -> Dict:
        return {
            'type': 'transaction',
            'signature': transaction.signature,
            'block_hash': transaction.block_hash,
            'previous_block_hash': transaction.previous_block_hash,
            'block_number': transaction.block_number,
            'block_timestamp': transaction.block_timestamp,
            'fee': transaction.fee,
            'status': transaction.status,
            'err': json.dumps(transaction.err),
            'accounts': json.dumps(transaction.accounts),
            'log_messages': json.dumps(transaction.log_messages),
            'balance_changes': json.dumps([
                self.balance_change_to_dict(e)
                for e in transaction.balance_changes
            ]),
            'pre_token_balances': json.dumps(transaction.pre_token_balances),
            'post_token_balances': json.dumps(transaction.post_token_balances),
        }

    def from_dict(self, dict: Dict) -> Transaction:
        transaction = Transaction()

        transaction.signature = dict.get('signature')
        transaction.block_hash = dict.get('block_hash')
        transaction.previous_block_hash = dict.get('previous_block_hash')
        transaction.block_number = dict.get('block_number')
        transaction.block_timestamp = dict.get('block_timestamp')
        transaction.fee = dict.get('fee')
        transaction.status = dict.get('status')
        transaction.accounts = json.loads(dict.get('accounts'))

        return transaction
