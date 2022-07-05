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
from typing import Dict

from solanaetl.domain.block import Block
from solanaetl.mappers.transaction_mapper import TransactionMapper


class BlockMapper(object):
    def __init__(self, transaction_mapper=None):
        if transaction_mapper is None:
            self.transaction_mapper = TransactionMapper()
        else:
            self.transaction_mapper = transaction_mapper

    def from_json_dict(self, json_dict: Dict) -> Block:
        block = Block()
        block.number = int(json_dict.get('parentSlot')) + 1
        block.hash = json_dict.get('blockhash')
        block.previous_block_hash = json_dict.get('previousBlockhash')
        block.timestamp = json_dict.get('blockTime')
        block.height = json_dict.get('blockHeight')

        if 'rewards' in json_dict:
            rewards = json_dict.get('rewards')
            block.rewards = rewards
            leader = next(reward for reward in rewards
                          if reward.get('rewardType') == 'Fee') if len(rewards) > 0 else None
            if leader is not None:
                block.leader_reward = leader.get('lamports')
                block.leader = leader.get('pubkey')

        if 'transactions' in json_dict:
            block.transactions = [
                self.transaction_mapper.from_json_dict(
                    tx,
                    block_timestamp=block.timestamp,
                    block_number=block.number,
                    block_hash=block.hash,
                )
                for tx in json_dict['transactions']
                if isinstance(tx, dict)
            ]
            block.transaction_count = len(json_dict.get('transactions'))
        elif 'signatures' in json_dict:
            block.transaction_count = len(json_dict.get('signatures'))

        return block

    def to_dict(self, block: Block) -> Dict:
        return {
            'type': 'block',
            'number': block.number,
            'height': block.height,
            'hash': block.hash,
            'previous_block_hash': block.previous_block_hash,
            'timestamp': block.timestamp,
            'transaction_count': block.transaction_count,
            'rewards': json.dumps(block.rewards),
            'leader_reward': block.leader_reward,
            'leader': block.leader,
        }
