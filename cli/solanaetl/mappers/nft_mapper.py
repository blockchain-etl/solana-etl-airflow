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

from solanaetl.domain.nft import Nft


class NftMapper(object):
    def metaplex_metadata_to_nft(self, metadata: dict) -> Nft:
        nft = Nft()
        nft.mint = metadata.get('mint')
        nft.update_authority = metadata.get('update_authority')
        nft.name = metadata.get('data').get('name')
        nft.symbol = metadata.get('data').get('symbol')
        nft.uri = metadata.get('data').get('uri')
        nft.seller_fee_basis_points = metadata.get(
            'data').get('seller_fee_basis_points')
        creators = metadata.get('data').get('creators')
        verified = metadata.get('data').get('verified')
        share = metadata.get('data').get('share')
        nft.creators = [
            {
                'address': creator.decode("utf-8"),
                'verified': verified[idx],
                'share': share[idx],
            }
            for idx, creator in enumerate(creators)
        ]
        nft.primary_sale_happened = metadata.get('primary_sale_happened')
        nft.is_mutable = metadata.get('is_mutable')

        return nft

    def nft_to_dict(self, nft: Nft) -> dict:
        return {
            'type': 'nft',
            'mint': nft.mint,
            'update_authority': nft.update_authority,
            'name': nft.name,
            'symbol': nft.symbol,
            'uri': nft.uri,
            'seller_fee_basis_points': nft.seller_fee_basis_points,
            'creators': json.dumps(nft.creators),
            'primary_sale_happened': nft.primary_sale_happened,
            'is_mutable': nft.is_mutable,
        }
