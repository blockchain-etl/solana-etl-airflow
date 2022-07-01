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

import os
from typing import Dict
from solanaetl.decoder.mango_markets_v3 import MangoMarketsV3ProgramDecoder

from solanaetl.decoder.program_decoder import ProgramDecoder
from solanaetl.decoder.serum_dex_v3 import SerumDexV3ProgramDecoder
from solanaetl.domain.instruction import Instruction

# default value is mainnet address
SERUM_DEX_V3 = os.getenv(
    'SERUM_DEX_V3', '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin')
MANGO_MARKETS_V3 = os.getenv(
    'MANGO_MARKETS_V3', 'mv3ekLzLbnVPNxjSKvqBpU3ZeZXPQdEC3bp5MDEBG68')

# Put your decoder here
PROGRAM_DECODER: Dict[str, ProgramDecoder] = {
    SERUM_DEX_V3: SerumDexV3ProgramDecoder(),
    MANGO_MARKETS_V3: MangoMarketsV3ProgramDecoder(),
}


class InstructionParser(object):

    def parse(self, instruction: Instruction):
        if instruction.program_id in PROGRAM_DECODER:
            decoder = PROGRAM_DECODER.get(instruction.program_id)
            instruction.program = decoder.name
            instruction.instruction_type, instruction.params = decoder.decode(
                instruction=instruction)

        return instruction
