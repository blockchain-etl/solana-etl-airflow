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


from lib2to3.pgen2 import token

from solanaetl.domain.instruction import Instruction
from solanaetl.domain.token_transfer import TokenTransfer

TOKEN_PROGRAM = 'spl-token'
SYSTEM_PROGRAM = 'system'
TRANSFER = 'transfer'
TRANSFER_CHECKED = 'transferChecked'
BURN = 'burn'
BURN_CHECKED = 'burnChecked'
MINT_TO = 'mintTo'
MINT_TO_CHECKED = 'mintToChecked'


def extract_transfer_from_instruction(instruction: Instruction) -> TokenTransfer:
    token_transfer = TokenTransfer()

    if instruction.program == TOKEN_PROGRAM:
        if instruction.instruction_type == TRANSFER or instruction.instruction_type == TRANSFER_CHECKED:
            token_transfer.value = instruction.params.get('amount')
            token_transfer.source = instruction.params.get('source')
            token_transfer.destination = instruction.params.get('destination')
            token_transfer.authority = instruction.params.get('authority')
            token_transfer.transfer_type = 'spl-transfer'
        if instruction.instruction_type == TRANSFER_CHECKED:
            token_transfer.mint = instruction.params.get('mint')
            token_transfer.value = instruction.params.get(
                'tokenAmount').get('amount')
            token_transfer.decimals = instruction.params.get(
                'tokenAmount').get('decimals')

        if instruction.instruction_type == BURN or instruction.instruction_type == BURN_CHECKED:
            token_transfer.value = instruction.params.get('amount')
            token_transfer.mint = instruction.params.get('mint')
            token_transfer.transfer_type = 'burn'
        if instruction.instruction_type == BURN_CHECKED:
            token_transfer.decimals = instruction.params.get('decimals')

        if instruction.instruction_type == MINT_TO or instruction.instruction_type == MINT_TO_CHECKED:
            token_transfer.mint = instruction.params.get('mint')
            token_transfer.value = instruction.params.get('amount')
            token_transfer.mint_authority = instruction.params.get(
                'mintAuthority')
            token_transfer.transfer_type = 'mintTo'
        if instruction.instruction_type == MINT_TO_CHECKED:
            token_transfer.decimals = instruction.params.get('decimals')

    elif instruction.program == SYSTEM_PROGRAM and instruction.instruction_type == TRANSFER:
        token_transfer.value = instruction.params.get('lamports')
        token_transfer.source = instruction.params.get('source')
        token_transfer.destination = instruction.params.get('destination')
        token_transfer.transfer_type = 'transfer'

    else:
        return None

    if token_transfer.transfer_type is None:
        return None

    token_transfer.tx_signature = instruction.tx_signature

    return token_transfer
