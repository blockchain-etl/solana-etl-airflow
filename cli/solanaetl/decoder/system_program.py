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

from base58 import b58decode
from solanaetl.decoder.utils import decode_params, ns64, public_key, u32, u64

# See: https://docs.rs/solana-program/latest/src/solana_program/system_instruction.rs.html


def decode(data: str) -> Dict[str, object]:
    data_decoded = b58decode(data.encode())
    program_func_index, _ = u32(data_decoded)
    decoding_params = {
        # CreateAccount
        #
        # Account references
        #   0. `[WRITE, SIGNER]` Funding account
        #   1. `[WRITE, SIGNER]` New account
        0: {
            "instruction": u32,
            "lamports": ns64,
            "space": ns64,
            "program_id": public_key,
        },
        # Assign
        #
        # Account references
        #   0. `[WRITE, SIGNER]` Assigned account public key
        1: {
            "instruction": u32,
            "program_id": public_key,
        },
        # Transfer
        #
        # Account references
        #   0. `[WRITE, SIGNER]` Funding account
        #   1. `[WRITE]` Recipient account
        2: {
            "instruction": u32,
            "lamports": u64,
        },
        # CreateAccountWithSeed
        3: {

        },
        # AdvanceNonceAccount
        4: {

        },
        # WithdrawNonceAccount
        5: {

        },
        # InitializeNonceAccount
        6: {

        },
        # AuthorizeNonceAccount
        7: {

        },
        # Allocate
        8: {

        },
        # AllocateWithSeed
        9: {

        },
        # AssignWithSeed
        10: {

        },
        # TransferWithSeed
        11: {

        },
        # UpgradeNonceAccount
        12: {

        },
    }

    return decode_params(data_decoded, decoding_params, program_func_index)
