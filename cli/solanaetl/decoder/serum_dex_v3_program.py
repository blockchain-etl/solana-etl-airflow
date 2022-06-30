# The MIT License (MIT)
# Copyright (c) 2022 Gamejam.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the 'Software'), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import enum

from base58 import b58decode
from solanaetl.decoder.utils import (decode_params, sint, u8, u16, u32, u64,
                                     u128)
from solanaetl.utils import safe_get

# See: https://github.com/project-serum/serum-dex/blob/master/dex/src/instruction.rs


class SerumDexV3Instruction(enum.Enum):
    initializeMarket = 0
    newOrder = 1
    matchOrders = 2
    consumeEvents = 3
    cancelOrder = 4
    settleFunds = 5
    cancelOrderByClientId = 6
    disableMarket = 7
    sweepFees = 8
    newOrderV2 = 9
    newOrderV3 = 10
    cancelOrderV2 = 11
    cancelOrderByClientIdV2 = 12
    sendTake = 13
    closeOpenOrders = 14
    initOpenOrders = 15
    prune = 16
    consumeEventsPermissioned = 17
    cancelOrdersByClientIds = 18
    replaceOrderByClientId = 19
    replaceOrdersByClientIds = 20


def decode(data: str, accounts: list[str] = []) -> dict[str, object]:
    data_decoded = b58decode(data.encode())
    data_decoded = data_decoded[1:]  # versioned_bytes
    program_func_index, _ = u32(data_decoded)
    # TODO: Fill all params to decode
    decoding_params = {
        SerumDexV3Instruction.initializeMarket.value: {
            'instruction': u32,
            'coin_lot_size': u64,
            'pc_lot_size': u64,
            'fee_rate_bps': u16,
            'vault_signer_nonce': u64,
            'pc_dust_threshold': u64,
            'market': lambda: safe_get(accounts, 0),
            'request_queue': lambda: safe_get(accounts, 1),
            'event_queue': lambda: safe_get(accounts, 2),
            'bids': lambda: safe_get(accounts, 3),
            'asks': lambda: safe_get(accounts, 4),
            'coin_currency': lambda: safe_get(accounts, 5),
            'price_currency': lambda: safe_get(accounts, 6),
            'coin_currency_mint': lambda: safe_get(accounts, 7),
            'price_currency_mint': lambda: safe_get(accounts, 8),
            'rent_sysvar': lambda: safe_get(accounts, 9),
            'open_orders_market_authority': lambda: safe_get(accounts, 10),
            'prune_authority': lambda: safe_get(accounts, 11),
            'crank_authority': lambda: safe_get(accounts, 12),
        },
        SerumDexV3Instruction.newOrder.value: {
            'instruction': u32,
            'side': u32,
            'limit_price': u64,
            'max_qty': u64,
            'order_type': u32,
            'client_id': u64,
            'market': lambda: safe_get(accounts, 0),
            'open_orders': lambda: safe_get(accounts, 1),
            'request_queue': lambda: safe_get(accounts, 2),
            'paying': lambda: safe_get(accounts, 3),
            'open_opders_owner': lambda: safe_get(accounts, 4),
            'coin_vault': lambda: safe_get(accounts, 5),
            'pc_vault': lambda: safe_get(accounts, 6),
            'token_program': lambda: safe_get(accounts, 7),
            'rent_sysvar': lambda: safe_get(accounts, 8),
            'srm': lambda: safe_get(accounts, 9),
        },
        SerumDexV3Instruction.matchOrders.value: {
            'instruction': u32,
            'limit': u16,
            'market': lambda: safe_get(accounts, 0),
            'request_queue': lambda: safe_get(accounts, 1),
            'event_queue': lambda: safe_get(accounts, 2),
            'bids': lambda: safe_get(accounts, 3),
            'asks': lambda: safe_get(accounts, 4),
        },
        SerumDexV3Instruction.consumeEvents.value: {
            'instruction': u32,
            'limit': u16,
            'open_orders': lambda: sorted(list(set(accounts))),
            'market': lambda: safe_get(accounts, len(accounts) - 4),
            'event_queue': lambda: safe_get(accounts, len(accounts) - 3),
        },
        SerumDexV3Instruction.cancelOrder.value: {
            'instruction': u32,
            'side': u32,
            'order_id': u128,
            'owner': u64,
            'owner_slot': u8,
            'market': lambda: safe_get(accounts, 0),
            'open_orders': lambda: safe_get(accounts, 1),
            'request_queue': lambda: safe_get(accounts, 2),
            'open_orders_owner': lambda: safe_get(accounts, 3),
        },
        SerumDexV3Instruction.settleFunds.value: {
            'instruction': u32,
            'market': lambda: safe_get(accounts, 0),
            'open_orders': lambda: safe_get(accounts, 1),
            'open_orders_owner': lambda: safe_get(accounts, 2),
            'coin_vault': lambda: safe_get(accounts, 3),
            'pc_vault': lambda: safe_get(accounts, 4),
            'coin_wallet': lambda: safe_get(accounts, 5),
            'pc_wallet': lambda: safe_get(accounts, 6),
            'vault_signer': lambda: safe_get(accounts, 7),
            'token_program': lambda: safe_get(accounts, 8),
            'ref_pc_wallet': lambda: safe_get(accounts, 9),
        },
        SerumDexV3Instruction.cancelOrderByClientId.value: {
            'instruction': u32,
            'client_id': u64,
            'market': lambda: safe_get(accounts, 0),
            'open_orders': lambda: safe_get(accounts, 1),
            'request_queue': lambda: safe_get(accounts, 2),
            'open_orders_owner': lambda: safe_get(accounts, 3),
        },
        SerumDexV3Instruction.disableMarket.value: {
            'instruction': u32,
            'market': lambda: safe_get(accounts, 0),
            'disable_authority': lambda: safe_get(accounts, 1),
        },
        SerumDexV3Instruction.sweepFees.value: {
            'instruction': u32,
            'market': lambda: safe_get(accounts, 0),
            'pc_vault': lambda: safe_get(accounts, 1),
            'fee_sweeping_authority': lambda: safe_get(accounts, 2),
            'fee_receivable': lambda: safe_get(accounts, 3),
            'vault_signer': lambda: safe_get(accounts, 4),
            'token_program': lambda: safe_get(accounts, 5),
        },
        SerumDexV3Instruction.newOrderV2.value: {
            'instruction': u32,
            'side': u32,
            'limit_price': u64,
            'max_qty': u64,
            'order_type': u32,
            'client_id': u64,
            'self_trade_behavior': u32,
            'market': lambda: safe_get(accounts, 0),
            'open_orders': lambda: safe_get(accounts, 1),
            'request_queue': lambda: safe_get(accounts, 2),
            'paying': lambda: safe_get(accounts, 3),
            'open_opders_owner': lambda: safe_get(accounts, 4),
            'coin_vault': lambda: safe_get(accounts, 5),
            'pc_vault': lambda: safe_get(accounts, 6),
            'token_program': lambda: safe_get(accounts, 7),
            'rent_sysvar': lambda: safe_get(accounts, 8),
            'srm': lambda: safe_get(accounts, 9),
        },
        SerumDexV3Instruction.newOrderV3.value: {
            'instruction': u32,
            'side': u32,
            'limit_price': u64,
            'max_coin_qty': u64,
            'max_native_pc_qty_including_fees': u64,
            'self_trade_behavior': u32,
            'order_type': u32,
            'client_id': u64,
            'limit': u16,
            'max_ts': lambda data, offset: sint(data, 64, offset),
            'market': lambda: safe_get(accounts, 0),
            'open_orders': lambda: safe_get(accounts, 1),
            'request_queue': lambda: safe_get(accounts, 2),
            'paying': lambda: safe_get(accounts, 3),
            'open_opders_owner': lambda: safe_get(accounts, 4),
            'coin_vault': lambda: safe_get(accounts, 5),
            'pc_vault': lambda: safe_get(accounts, 6),
            'token_program': lambda: safe_get(accounts, 7),
            'rent_sysvar': lambda: safe_get(accounts, 8),
            'srm': lambda: safe_get(accounts, 9),
        },
        SerumDexV3Instruction.cancelOrderV2.value: {
            'instruction': u32,
            'side': u32,
            'order_id': u128,
            'market': lambda: safe_get(accounts, 0),
            'bids': lambda: safe_get(accounts, 1),
            'asks': lambda: safe_get(accounts, 2),
            'open_orders': lambda: safe_get(accounts, 3),
            'owner': lambda: safe_get(accounts, 4),
            'event_queue': lambda: safe_get(accounts, 5),
        },
        SerumDexV3Instruction.cancelOrderByClientIdV2.value: {
            'instruction': u32,
            'client_id': u64,
            'market': lambda: safe_get(accounts, 0),
            'bids': lambda: safe_get(accounts, 1),
            'asks': lambda: safe_get(accounts, 2),
            'open_orders': lambda: safe_get(accounts, 3),
            'owner': lambda: safe_get(accounts, 4),
            'event_queue': lambda: safe_get(accounts, 5),
        },
        SerumDexV3Instruction.sendTake.value: {
            'instruction': u32,
            'side': u32,
            'limit_price': u64,
            'max_coin_qty': u64,
            'max_native_pc_qty_including_fees': u64,
            'min_coin_qty': u64,
            'min_native_pc_qty_including_fees': u64,
            'limit': u16,
            'market': lambda: safe_get(accounts, 0),
            'request_queue': lambda: safe_get(accounts, 1),
            'event_queue': lambda: safe_get(accounts, 2),
            'bids': lambda: safe_get(accounts, 3),
            'asks': lambda: safe_get(accounts, 4),
            'coin_wallet': lambda: safe_get(accounts, 5),
            'pc_wallet': lambda: safe_get(accounts, 6),
            'signer': lambda: safe_get(accounts, 7),
            'coin_vault': lambda: safe_get(accounts, 8),
            'pc_vault': lambda: safe_get(accounts, 9),
            'token_program': lambda: safe_get(accounts, 10),
            'srm': lambda: safe_get(accounts, 11),
        },
        SerumDexV3Instruction.closeOpenOrders.value: {
            'instruction': u32,
            'open_orders': lambda: safe_get(accounts, 0),
            'open_opders_owner': lambda: safe_get(accounts, 1),
            'market': lambda: safe_get(accounts, 2),
        },
        SerumDexV3Instruction.initOpenOrders.value: {
            'instruction': u32,
            'market': lambda: safe_get(accounts, 0),
            'bids': lambda: safe_get(accounts, 1),
            'asks': lambda: safe_get(accounts, 2),
            'prune_authority': lambda: safe_get(accounts, 3),
            'open_orders': lambda: safe_get(accounts, 4),
            'open_opders_owner': lambda: safe_get(accounts, 5),
            'event_queue': lambda: safe_get(accounts, 6),
        },
        SerumDexV3Instruction.prune.value: {
            'instruction': u32,
            'limit': u16,
            'market': lambda: safe_get(accounts, 0),
            'bids': lambda: safe_get(accounts, 1),
            'asks': lambda: safe_get(accounts, 2),
            'prune_authority': lambda: safe_get(accounts, 3),
            'open_orders': lambda: safe_get(accounts, 4),
            'open_opders_owner': lambda: safe_get(accounts, 5),
            'event_queue': lambda: safe_get(accounts, 6),
        },
        SerumDexV3Instruction.consumeEventsPermissioned.value: {
            'instruction': u32,
            'limit': u16,
            'open_orders': lambda: sorted(list(set(accounts))),
            'market': lambda: safe_get(accounts, len(accounts) - 3),
            'event_queue': lambda: safe_get(accounts, len(accounts) - 2),
            'crank_authority': lambda: safe_get(accounts, len(accounts) - 1),
        },
        SerumDexV3Instruction.cancelOrdersByClientIds.value: {
            'instruction': u32,
            # TODO: chunk client_ids
            'market': lambda: safe_get(accounts, 0),
            'bids': lambda: safe_get(accounts, 1),
            'asks': lambda: safe_get(accounts, 2),
            'open_orders': lambda: safe_get(accounts, 3),
            'open_opders_owner': lambda: safe_get(accounts, 4),
            'event_queue': lambda: safe_get(accounts, 5),
        },
        SerumDexV3Instruction.replaceOrderByClientId.value: {
            'instruction': u32,
            'side': u32,
            'limit_price': u64,
            'max_coin_qty': u64,
            'max_native_pc_qty_including_fees': u64,
            'self_trade_behavior': u32,
            'order_type': u32,
            'client_id': u64,
            'limit': u16,
            'max_ts': lambda data, offset: sint(data, 64, offset),
            'market': lambda: safe_get(accounts, 0),
            'open_orders': lambda: safe_get(accounts, 1),
            'request_queue': lambda: safe_get(accounts, 2),
            'event_queue': lambda: safe_get(accounts, 3),
            'bids': lambda: safe_get(accounts, 4),
            'asks': lambda: safe_get(accounts, 5),
            'paying': lambda: safe_get(accounts, 6),
            'open_opders_owner': lambda: safe_get(accounts, 7),
            'coin_vault': lambda: safe_get(accounts, 8),
            'pc_vault': lambda: safe_get(accounts, 9),
            'token_program': lambda: safe_get(accounts, 10),
            'rent_sysvar': lambda: safe_get(accounts, 11),
            'srm': lambda: safe_get(accounts, 12),
        },
        SerumDexV3Instruction.replaceOrdersByClientIds.value: {
            'instruction': u32,
            # TODO: chunk new_orders
            'market': lambda: safe_get(accounts, 0),
            'open_orders': lambda: safe_get(accounts, 1),
            'request_queue': lambda: safe_get(accounts, 2),
            'event_queue': lambda: safe_get(accounts, 3),
            'bids': lambda: safe_get(accounts, 4),
            'asks': lambda: safe_get(accounts, 5),
            'paying': lambda: safe_get(accounts, 6),
            'open_opders_owner': lambda: safe_get(accounts, 7),
            'coin_vault': lambda: safe_get(accounts, 8),
            'pc_vault': lambda: safe_get(accounts, 9),
            'token_program': lambda: safe_get(accounts, 10),
            'rent_sysvar': lambda: safe_get(accounts, 11),
            'srm': lambda: safe_get(accounts, 12),
        },
    }

    return decode_params(data_decoded, decoding_params, program_func_index, program='Serum DEX V3')
