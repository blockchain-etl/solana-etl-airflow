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

from typing import Dict, List

from solanaetl.domain.account import Account
from solanaetl.domain.instruction import Instruction


class BalanceChange(object):
    def __init__(self) -> None:
        self.account = None
        self.before = None
        self.after = None


class Transaction(object):
    def __init__(self) -> None:
        self.signature = None
        self.block_hash = None
        self.previous_block_hash = None
        self.block_number = None
        self.block_timestamp = None
        self.fee = None
        self.status = None
        self.err = None
        self.accounts: List[Dict] = []
        self.instructions: List[Instruction] = []
        self.log_messages: List[str] = []
        self.balance_changes: List[int] = []
        self.pre_token_balances = None
        self.post_token_balances = None
