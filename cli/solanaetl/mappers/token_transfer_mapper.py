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


from typing import Dict

from solanaetl.domain.token_transfer import TokenTransfer


class TokenTransferMapper(object):

    def to_dict(self, token_transfer: TokenTransfer) -> Dict:
        return {
            'type': 'token_transfer',
            'source': token_transfer.source,
            'destination': token_transfer.destination,
            'authority': token_transfer.authority,
            'value': token_transfer.value,
            'decimals': token_transfer.decimals,
            'mint': token_transfer.mint,
            'mint_authority': token_transfer.mint_authority,
            'transfer_type':  token_transfer.transfer_type,
            'tx_signature': token_transfer.tx_signature,
        }
