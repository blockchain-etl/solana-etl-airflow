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


from curses import beep
import json
from solanaetl.domain.instruction import Instruction
from solanaetl.domain.transaction import BalanceChange, TokenBalanceChange, Transaction
from solanaetl.mappers.account_mapper import AccountMapper
from solanaetl.mappers.instruction_mapper import InstructionMapper


class TransactionMapper(object):
    def __init__(self, instruction_mapper=None, account_mapper=None) -> None:
        self.instruction_mapper = instruction_mapper if instruction_mapper is not None else InstructionMapper()
        self.account_mapper = account_mapper if account_mapper is not None else AccountMapper()

    def json_dict_to_transaction(self, json_dict: dict, **kwargs):
        transaction = Transaction()

        transaction.block_hash = kwargs.get('block_hash')
        transaction.block_number = kwargs.get('block_number')
        transaction.block_timestamp = kwargs.get('block_timestamp')

        tx_json: dict = json_dict.get('transaction')
        instructions: list[Instruction] = []
        if tx_json is not None:
            transaction.signature = tx_json.get('signatures')[0]
            transaction.accounts = tx_json.get('message').get('accountKeys')
            transaction.previous_block_hash = tx_json.get(
                'message').get('recentBlockhash')

            if 'instructions' in tx_json.get('message'):
                instructions.extend([
                    self.instruction_mapper.json_dict_to_instruction(
                        instruction, tx_signature=transaction.signature, index=index)
                    for index, instruction in enumerate(tx_json.get('message').get('instructions'))
                ])

        # meta
        tx_meta_json: dict = json_dict.get('meta')
        if tx_meta_json is not None:
            transaction.fee = tx_meta_json.get('fee')
            tx_err = tx_meta_json.get('err')
            transaction.status = "Success" if tx_err is None else "Fail"

            if 'innerInstructions' in tx_meta_json:
                instructions.extend([
                    self.instruction_mapper.json_dict_to_instruction(
                        instruction, tx_signature=transaction.signature, index=index, parent_index=inner_instruction.get('index'))
                    for inner_instruction in tx_meta_json.get('innerInstructions')
                    for index, instruction in enumerate(inner_instruction.get('instructions'))
                ])

            if 'logMessages' in tx_meta_json:
                transaction.log_messages = tx_meta_json.get('logMessages')

            balance_changes: list[BalanceChange] = []
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

            token_balance_changes: list[TokenBalanceChange] = []
            if 'postTokenBalances' in tx_meta_json and 'preTokenBalances' in tx_meta_json:
                post_token_balances = tx_meta_json.get('postTokenBalances')
                pre_token_balances = tx_meta_json.get('preTokenBalances')
                pre_token_balances = {
                    e.get('accountIndex'): e for e in pre_token_balances}

                for post_balance in post_token_balances:
                    account_index = post_balance.get('accountIndex')

                    account = transaction.accounts[account_index]
                    token_balance_change = TokenBalanceChange()
                    token_balance_change.account = account.get('pubkey')
                    token_balance_change.owner = post_balance.get('owner')
                    token_balance_change.mint = post_balance.get('mint')

                    token_balance_change.after = post_balance.get(
                        'uiTokenAmount').get('amount')
                    token_balance_change.after_decimals = post_balance.get(
                        'uiTokenAmount').get('decimals')

                    pre_balance = pre_token_balances.get(account_index)
                    if pre_balance is not None:
                        token_balance_change.before = pre_balance.get(
                            'uiTokenAmount').get('amount')
                        token_balance_change.before_decimals = pre_balance.get(
                            'uiTokenAmount').get('decimals')
                    else:
                        token_balance_change.before = 0
                        token_balance_change.before_decimals = token_balance_change.after_decimals

                    token_balance_changes.append(token_balance_change)

                transaction.token_balance_changes = token_balance_changes

        transaction.instructions = instructions

        return transaction

    def balance_change_to_dict(self, balance_change: BalanceChange):
        return {
            'account': balance_change.account,
            'before': balance_change.before,
            'after': balance_change.after,
        }

    def token_balance_change_to_dict(self, token_balance_change: TokenBalanceChange):
        return {
            'account': token_balance_change.account,
            'owner': token_balance_change.owner,
            'mint': token_balance_change.mint,
            'before': token_balance_change.before,
            'before_decimals': token_balance_change.before_decimals,
            'after': token_balance_change.after,
            'after_decimals': token_balance_change.after_decimals,
        }

    def transaction_to_dict(self, transaction: Transaction):
        return {
            'type': 'transaction',
            'signature': transaction.signature,
            'block_hash': transaction.block_hash,
            'previous_block_hash': transaction.previous_block_hash,
            'block_number': transaction.block_number,
            'block_timestamp': transaction.block_timestamp,
            'fee': transaction.fee,
            'status': transaction.status,
            'accounts': json.dumps(transaction.accounts),
            'log_messages': json.dumps(transaction.log_messages),
            'balance_changes': json.dumps([
                self.balance_change_to_dict(e)
                for e in transaction.balance_changes
            ]),
            'token_balance_changes': json.dumps([
                self.token_balance_change_to_dict(e)
                for e in transaction.token_balance_changes
            ])
        }

    def dict_to_transaction(self, dict: dict):
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
