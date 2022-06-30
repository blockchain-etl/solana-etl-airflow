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

from solanaetl.decoder import serum_dex_v3_program
from solanaetl.domain.instruction import Instruction

SERUM_DEX_V3 = os.getenv(
    'SERUM_DEX_V3', '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin')

# TODO: should restructure for easy to register custom program.
class InstructionParser(object):
    def parse(self, instruction: Instruction):
        if instruction.program_id == SERUM_DEX_V3:
            instruction.program = 'serum-dex-v3'
            instruction.params = serum_dex_v3_program.decode(
                data=instruction.data, accounts=instruction.accounts)
            instruction.instruction_type = serum_dex_v3_program.SerumDexV3Instruction(
                instruction.params.get('instruction')).name

        if 'instruction' in instruction.params:
            del instruction.params['instruction']

        return instruction
