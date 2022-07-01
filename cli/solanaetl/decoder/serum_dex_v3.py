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
import sys
from typing import Any, Callable, Dict, Tuple

from solanaetl.decoder.buffer_layout import (iter_blob, sint, u8, u16, u32,
                                             u64, u128)
from solanaetl.decoder.program_decoder import ProgramDecoder
from solanaetl.domain.instruction import Instruction
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


class SerumDexV3ProgramDecoder(ProgramDecoder):

    def __init__(self) -> None:
        super().__init__('serum-dex-v3', can_decode=True)

    def discrim(self) -> Callable[[bytes, int], Tuple[int, int]]:
        return lambda data, offset: u32(data, offset)

    def instruction(self, discrim: int) -> str:
        return SerumDexV3Instruction(discrim).name

    def params(self) -> Dict[int, Dict[str, Any]]:
        return {
            SerumDexV3Instruction.initializeMarket.value: {
                'coin_lot_size': u64,
                'pc_lot_size': u64,
                'fee_rate_bps': u16,
                'vault_signer_nonce': u64,
                'pc_dust_threshold': u64,
                'market': lambda accounts: safe_get(accounts, 0),
                'request_queue': lambda accounts: safe_get(accounts, 1),
                'event_queue': lambda accounts: safe_get(accounts, 2),
                'bids': lambda accounts: safe_get(accounts, 3),
                'asks': lambda accounts: safe_get(accounts, 4),
                'coin_currency': lambda accounts: safe_get(accounts, 5),
                'price_currency': lambda accounts: safe_get(accounts, 6),
                'coin_currency_mint': lambda accounts: safe_get(accounts, 7),
                'price_currency_mint': lambda accounts: safe_get(accounts, 8),
                'rent_sysvar': lambda accounts: safe_get(accounts, 9),
                'open_orders_market_authority': lambda accounts: safe_get(accounts, 10),
                'prune_authority': lambda accounts: safe_get(accounts, 11),
                'crank_authority': lambda accounts: safe_get(accounts, 12),
            },
            SerumDexV3Instruction.newOrder.value: {
                'side': u32,
                'limit_price': u64,
                'max_qty': u64,
                'order_type': u32,
                'client_id': u64,
                'market': lambda accounts: safe_get(accounts, 0),
                'open_orders': lambda accounts: safe_get(accounts, 1),
                'request_queue': lambda accounts: safe_get(accounts, 2),
                'paying': lambda accounts: safe_get(accounts, 3),
                'open_opders_owner': lambda accounts: safe_get(accounts, 4),
                'coin_vault': lambda accounts: safe_get(accounts, 5),
                'pc_vault': lambda accounts: safe_get(accounts, 6),
                'token_program': lambda accounts: safe_get(accounts, 7),
                'rent_sysvar': lambda accounts: safe_get(accounts, 8),
                'srm': lambda accounts: safe_get(accounts, 9),
            },
            SerumDexV3Instruction.matchOrders.value: {
                'limit': u16,
                'market': lambda accounts: safe_get(accounts, 0),
                'request_queue': lambda accounts: safe_get(accounts, 1),
                'event_queue': lambda accounts: safe_get(accounts, 2),
                'bids': lambda accounts: safe_get(accounts, 3),
                'asks': lambda accounts: safe_get(accounts, 4),
            },
            SerumDexV3Instruction.consumeEvents.value: {
                'limit': u16,
                'open_orders': lambda accounts: sorted(list(set(accounts))),
                'market': lambda accounts: safe_get(accounts, len(accounts) - 4),
                'event_queue': lambda accounts: safe_get(accounts, len(accounts) - 3),
            },
            SerumDexV3Instruction.cancelOrder.value: {
                'side': u32,
                'order_id': u128,
                'owner': u64,
                'owner_slot': u8,
                'market': lambda accounts: safe_get(accounts, 0),
                'open_orders': lambda accounts: safe_get(accounts, 1),
                'request_queue': lambda accounts: safe_get(accounts, 2),
                'open_orders_owner': lambda accounts: safe_get(accounts, 3),
            },
            SerumDexV3Instruction.settleFunds.value: {
                'market': lambda accounts: safe_get(accounts, 0),
                'open_orders': lambda accounts: safe_get(accounts, 1),
                'open_orders_owner': lambda accounts: safe_get(accounts, 2),
                'coin_vault': lambda accounts: safe_get(accounts, 3),
                'pc_vault': lambda accounts: safe_get(accounts, 4),
                'coin_wallet': lambda accounts: safe_get(accounts, 5),
                'pc_wallet': lambda accounts: safe_get(accounts, 6),
                'vault_signer': lambda accounts: safe_get(accounts, 7),
                'token_program': lambda accounts: safe_get(accounts, 8),
                'ref_pc_wallet': lambda accounts: safe_get(accounts, 9),
            },
            SerumDexV3Instruction.cancelOrderByClientId.value: {
                'client_id': u64,
                'market': lambda accounts: safe_get(accounts, 0),
                'open_orders': lambda accounts: safe_get(accounts, 1),
                'request_queue': lambda accounts: safe_get(accounts, 2),
                'open_orders_owner': lambda accounts: safe_get(accounts, 3),
            },
            SerumDexV3Instruction.disableMarket.value: {
                'market': lambda accounts: safe_get(accounts, 0),
                'disable_authority': lambda accounts: safe_get(accounts, 1),
            },
            SerumDexV3Instruction.sweepFees.value: {
                'market': lambda accounts: safe_get(accounts, 0),
                'pc_vault': lambda accounts: safe_get(accounts, 1),
                'fee_sweeping_authority': lambda accounts: safe_get(accounts, 2),
                'fee_receivable': lambda accounts: safe_get(accounts, 3),
                'vault_signer': lambda accounts: safe_get(accounts, 4),
                'token_program': lambda accounts: safe_get(accounts, 5),
            },
            SerumDexV3Instruction.newOrderV2.value: {
                'side': u32,
                'limit_price': u64,
                'max_qty': u64,
                'order_type': u32,
                'client_id': u64,
                'self_trade_behavior': u32,
                'market': lambda accounts: safe_get(accounts, 0),
                'open_orders': lambda accounts: safe_get(accounts, 1),
                'request_queue': lambda accounts: safe_get(accounts, 2),
                'paying': lambda accounts: safe_get(accounts, 3),
                'open_opders_owner': lambda accounts: safe_get(accounts, 4),
                'coin_vault': lambda accounts: safe_get(accounts, 5),
                'pc_vault': lambda accounts: safe_get(accounts, 6),
                'token_program': lambda accounts: safe_get(accounts, 7),
                'rent_sysvar': lambda accounts: safe_get(accounts, 8),
                'srm': lambda accounts: safe_get(accounts, 9),
            },
            SerumDexV3Instruction.newOrderV3.value: {
                'side': u32,
                'limit_price': u64,
                'max_coin_qty': u64,
                'max_native_pc_qty_including_fees': u64,
                'self_trade_behavior': u32,
                'order_type': u32,
                'client_id': u64,
                'limit': u16,
                'max_ts': lambda data, offset: sint(data, 8, offset) if len(data) == 58 else (sys.maxsize, offset),
                'market': lambda accounts: safe_get(accounts, 0),
                'open_orders': lambda accounts: safe_get(accounts, 1),
                'request_queue': lambda accounts: safe_get(accounts, 2),
                'paying': lambda accounts: safe_get(accounts, 3),
                'open_opders_owner': lambda accounts: safe_get(accounts, 4),
                'coin_vault': lambda accounts: safe_get(accounts, 5),
                'pc_vault': lambda accounts: safe_get(accounts, 6),
                'token_program': lambda accounts: safe_get(accounts, 7),
                'rent_sysvar': lambda accounts: safe_get(accounts, 8),
                'srm': lambda accounts: safe_get(accounts, 9),
            },
            SerumDexV3Instruction.cancelOrderV2.value: {
                'side': u32,
                'order_id': u128,
                'market': lambda accounts: safe_get(accounts, 0),
                'bids': lambda accounts: safe_get(accounts, 1),
                'asks': lambda accounts: safe_get(accounts, 2),
                'open_orders': lambda accounts: safe_get(accounts, 3),
                'owner': lambda accounts: safe_get(accounts, 4),
                'event_queue': lambda accounts: safe_get(accounts, 5),
            },
            SerumDexV3Instruction.cancelOrderByClientIdV2.value: {
                'client_id': u64,
                'market': lambda accounts: safe_get(accounts, 0),
                'bids': lambda accounts: safe_get(accounts, 1),
                'asks': lambda accounts: safe_get(accounts, 2),
                'open_orders': lambda accounts: safe_get(accounts, 3),
                'owner': lambda accounts: safe_get(accounts, 4),
                'event_queue': lambda accounts: safe_get(accounts, 5),
            },
            SerumDexV3Instruction.sendTake.value: {
                'side': u32,
                'limit_price': u64,
                'max_coin_qty': u64,
                'max_native_pc_qty_including_fees': u64,
                'min_coin_qty': u64,
                'min_native_pc_qty_including_fees': u64,
                'limit': u16,
                'market': lambda accounts: safe_get(accounts, 0),
                'request_queue': lambda accounts: safe_get(accounts, 1),
                'event_queue': lambda accounts: safe_get(accounts, 2),
                'bids': lambda accounts: safe_get(accounts, 3),
                'asks': lambda accounts: safe_get(accounts, 4),
                'coin_wallet': lambda accounts: safe_get(accounts, 5),
                'pc_wallet': lambda accounts: safe_get(accounts, 6),
                'signer': lambda accounts: safe_get(accounts, 7),
                'coin_vault': lambda accounts: safe_get(accounts, 8),
                'pc_vault': lambda accounts: safe_get(accounts, 9),
                'token_program': lambda accounts: safe_get(accounts, 10),
                'srm': lambda accounts: safe_get(accounts, 11),
            },
            SerumDexV3Instruction.closeOpenOrders.value: {
                'open_orders': lambda accounts: safe_get(accounts, 0),
                'open_opders_owner': lambda accounts: safe_get(accounts, 1),
                'market': lambda accounts: safe_get(accounts, 2),
            },
            SerumDexV3Instruction.initOpenOrders.value: {
                'market': lambda accounts: safe_get(accounts, 0),
                'bids': lambda accounts: safe_get(accounts, 1),
                'asks': lambda accounts: safe_get(accounts, 2),
                'prune_authority': lambda accounts: safe_get(accounts, 3),
                'open_orders': lambda accounts: safe_get(accounts, 4),
                'open_opders_owner': lambda accounts: safe_get(accounts, 5),
                'event_queue': lambda accounts: safe_get(accounts, 6),
            },
            SerumDexV3Instruction.prune.value: {
                'limit': u16,
                'market': lambda accounts: safe_get(accounts, 0),
                'bids': lambda accounts: safe_get(accounts, 1),
                'asks': lambda accounts: safe_get(accounts, 2),
                'prune_authority': lambda accounts: safe_get(accounts, 3),
                'open_orders': lambda accounts: safe_get(accounts, 4),
                'open_opders_owner': lambda accounts: safe_get(accounts, 5),
                'event_queue': lambda accounts: safe_get(accounts, 6),
            },
            SerumDexV3Instruction.consumeEventsPermissioned.value: {
                'limit': u16,
                'open_orders': lambda accounts: sorted(list(set(accounts))),
                'market': lambda accounts: safe_get(accounts, len(accounts) - 3),
                'event_queue': lambda accounts: safe_get(accounts, len(accounts) - 2),
                'crank_authority': lambda accounts: safe_get(accounts, len(accounts) - 1),
            },
            SerumDexV3Instruction.cancelOrdersByClientIds.value: {
                'client_ids': lambda data, offset: iter_blob(data, u64, n_items=len(data) // 8, offset=offset),
                'market': lambda accounts: safe_get(accounts, 0),
                'bids': lambda accounts: safe_get(accounts, 1),
                'asks': lambda accounts: safe_get(accounts, 2),
                'open_orders': lambda accounts: safe_get(accounts, 3),
                'open_opders_owner': lambda accounts: safe_get(accounts, 4),
                'event_queue': lambda accounts: safe_get(accounts, 5),
            },
            SerumDexV3Instruction.replaceOrderByClientId.value: {
                'side': u32,
                'limit_price': u64,
                'max_coin_qty': u64,
                'max_native_pc_qty_including_fees': u64,
                'self_trade_behavior': u32,
                'order_type': u32,
                'client_id': u64,
                'limit': u16,
                'max_ts': lambda data, offset: sint(data, 8, offset),
                'market': lambda accounts: safe_get(accounts, 0),
                'open_orders': lambda accounts: safe_get(accounts, 1),
                'request_queue': lambda accounts: safe_get(accounts, 2),
                'event_queue': lambda accounts: safe_get(accounts, 3),
                'bids': lambda accounts: safe_get(accounts, 4),
                'asks': lambda accounts: safe_get(accounts, 5),
                'paying': lambda accounts: safe_get(accounts, 6),
                'open_opders_owner': lambda accounts: safe_get(accounts, 7),
                'coin_vault': lambda accounts: safe_get(accounts, 8),
                'pc_vault': lambda accounts: safe_get(accounts, 9),
                'token_program': lambda accounts: safe_get(accounts, 10),
                'rent_sysvar': lambda accounts: safe_get(accounts, 11),
                'srm': lambda accounts: safe_get(accounts, 12),
            },
            SerumDexV3Instruction.replaceOrdersByClientIds.value: {
                # TODO: chunk new_orders
                'market': lambda accounts: safe_get(accounts, 0),
                'open_orders': lambda accounts: safe_get(accounts, 1),
                'request_queue': lambda accounts: safe_get(accounts, 2),
                'event_queue': lambda accounts: safe_get(accounts, 3),
                'bids': lambda accounts: safe_get(accounts, 4),
                'asks': lambda accounts: safe_get(accounts, 5),
                'paying': lambda accounts: safe_get(accounts, 6),
                'open_opders_owner': lambda accounts: safe_get(accounts, 7),
                'coin_vault': lambda accounts: safe_get(accounts, 8),
                'pc_vault': lambda accounts: safe_get(accounts, 9),
                'token_program': lambda accounts: safe_get(accounts, 10),
                'rent_sysvar': lambda accounts: safe_get(accounts, 11),
                'srm': lambda accounts: safe_get(accounts, 12),
            },
        }

    def decode(self, instruction: Instruction) -> Dict[str, Any]:
        # the first bytes is versioned bytes
        return super().decode(instruction, initial_offset=1)
