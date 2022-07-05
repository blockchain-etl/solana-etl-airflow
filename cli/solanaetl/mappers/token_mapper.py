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

from solanaetl.domain.token import Token


class TokenMapper(object):
    def from_metaplex_metadata(self, metadata: Dict, token_type: str = None, tx_signature: str = None) -> Token:
        token = Token()
        token.tx_signature = tx_signature
        token.token_type = token_type
        token.mint = metadata.get('mint')
        token.update_authority = metadata.get('update_authority')
        token.name = metadata.get('data').get('name')
        token.symbol = metadata.get('data').get('symbol')
        token.uri = metadata.get('data').get('uri')
        token.seller_fee_basis_points = metadata.get(
            'data').get('seller_fee_basis_points')
        creators = metadata.get('data').get('creators')
        verified = metadata.get('data').get('verified')
        share = metadata.get('data').get('share')
        token.creators = [
            {
                'address': creator.decode("utf-8"),
                'verified': verified[idx],
                'share': share[idx],
            }
            for idx, creator in enumerate(creators)
        ]
        token.primary_sale_happened = metadata.get('primary_sale_happened')
        token.is_mutable = metadata.get('is_mutable')

        return token

    def to_dict(self, token: Token) -> Dict:
        return {
            'type': 'token',
            'tx_signature': token.tx_signature,
            'token_type': token.token_type,
            'mint': token.mint,
            'update_authority': token.update_authority,
            'name': token.name,
            'symbol': token.symbol,
            'uri': token.uri,
            'seller_fee_basis_points': token.seller_fee_basis_points,
            'creators': json.dumps(token.creators),
            'primary_sale_happened': token.primary_sale_happened,
            'is_mutable': token.is_mutable,
        }
