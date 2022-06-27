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

from solanaetl.domain.account import Account


class AccountMapper(object):
    def json_dict_to_account(self, json_dict: dict):
        account = Account()
        account.pubkey = json_dict.get('pubkey')
        account.signer = json_dict.get('signer')
        account.writable = json_dict.get('writable')

        return account

    def account_to_dict(self, account: Account):
        return {
            'type': 'account',
            'pubkey': account.pubkey,
            'signer': account.signer,
            'writable': account.writable,
        }

    def tx_account_to_dict(self, tx_signature: str, account: Account):
        return dict(self.account_to_dict(account), **{'tx_signature': tx_signature})
