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


class Account(object):
    def __init__(self) -> None:
        self.pubkey = None
        self.tx_signature = None  # creation tx
        self.executable = None
        self.lamports = None
        self.owner = None
        self.rent_epoch = None
        self.data = None  # raw data
        # parsed data
        self.program = None
        self.space = None
        self.account_type = None
        # if type = token account
        self.is_native = None
        self.mint = None  # token address
        self.mint_authority = None
        self.owner = None
        self.state = None
        self.token_amount = None
        self.token_amount_decimals = None
        self.supply = None
        # if type = program
        self.program_data = None
        # if type = vote
        self.authorized_voters = None
        self.authorized_withdrawer = None
        self.prior_voters = None
        self.node_pubkey = None
        self.commission = None
        self.epoch_credits = None
        self.votes = None
        self.root_slot = None
        self.last_timestamp = None
