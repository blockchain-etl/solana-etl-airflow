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


import enum
from based58 import b58decode
from solanaetl.decoder.utils import decode_params, u8, u16, u32, u64, u128
from solanaetl.utils import safe_get

# See: https://github.com/project-serum/serum-dex/blob/master/dex/src/instruction.rs


class Instruction(enum.Enum):
    InitializeMarket = 0
    NewOrder = 1
    MatchOrders = 2
    ConsumeEvents = 3
    CancelOrder = 4
    SettleFunds = 5
    CancelOrderByClientId = 6
    DisableMarket = 7
    SweepFees = 8
    NewOrderV2 = 9
    NewOrderV3 = 10
    CancelOrderV2 = 11
    CancelOrderByClientIdV2 = 12
    SendTake = 13
    CloseOpenOrders = 14
    InitOpenOrders = 15
    Prune = 16
    ConsumeEventsPermissioned = 17
    CancelOrdersByClientIds = 18
    ReplaceOrderByClientId = 19
    ReplaceOrdersByClientIds = 20


def decode(data: str, accounts: list[str] = []) -> dict[str, object]:
    data_decoded = b58decode(data.encode())
    data_decoded = data_decoded[1:]
    program_func_index, _ = u8(data_decoded)
    # TODO: Fill all params to decode
    decoding_params = {
        Instruction.InitializeMarket.value: {
            'instruction': u8,
            'coin_lot_size': u64,
            'pc_lot_size': u64,
            'fee_rate_bps': u16,
            'vault_signer_nonce': u64,
            'pc_dust_threshold': u64,
        },
        Instruction.NewOrder.value: {
            'instruction': u8,
        },
        Instruction.MatchOrders.value: {
            'instruction': u8,
        },
        Instruction.ConsumeEvents.value: {
            'instruction': u8,
        },
        Instruction.CancelOrder.value: {
            'instruction': u8,
        },
        Instruction.SettleFunds.value: {
            'instruction': u8,
        },
        Instruction.CancelOrderByClientId.value: {
            'instruction': u8,
        },
        Instruction.DisableMarket.value: {
            'instruction': u8,
        },
        Instruction.SweepFees.value: {
            'instruction': u8,
        },
        Instruction.NewOrderV2.value: {
            'instruction': u8,
        },
        Instruction.NewOrderV3.value: {
            'instruction': u8,
        },
        Instruction.CancelOrderV2.value: {
            'instruction': u8,
            'side': u32,
            'order_id': u128,
            "market": safe_get(accounts, 0),
            "bids": safe_get(accounts, 1),
            "asks": safe_get(accounts, 2),
            "open_orders": safe_get(accounts, 3),
            "owner": safe_get(accounts, 4),
            "event_queue": safe_get(accounts, 5),
        },
        Instruction.CancelOrderByClientIdV2.value: {
            'instruction': u8,
        },
        Instruction.SendTake.value: {
            'instruction': u8,
        },
        Instruction.CloseOpenOrders.value: {
            'instruction': u8,
        },
        Instruction.InitOpenOrders.value: {
            'instruction': u8,
        },
        Instruction.Prune.value: {
            'name': Instruction.Prune.name,
            'instruction': u8,
        },
        Instruction.ConsumeEventsPermissioned.value: {
            'instruction': u8,
        },
        Instruction.CancelOrdersByClientIds.value: {
            'instruction': u8,
        },
        Instruction.ReplaceOrderByClientId.value: {
            'instruction': u8,
        },
        Instruction.ReplaceOrdersByClientIds.value: {
            'instruction': u8,
        },
    }

    return decode_params(data_decoded, decoding_params, program_func_index, program='Serum DEX V3')
