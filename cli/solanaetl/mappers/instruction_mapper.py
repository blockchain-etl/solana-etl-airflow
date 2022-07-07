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

from solanaetl.domain.instruction import Instruction


class InstructionMapper(object):
    def from_json_dict(self, json_dict: Dict, tx_signature: str, index: int, parent_index: int = None) -> Instruction:
        instruction = Instruction()
        instruction.tx_signature = tx_signature
        instruction.index = index
        instruction.parent_index = parent_index
        instruction.accounts = json_dict.get('accounts')
        instruction.data = json_dict.get('data')
        instruction.program = json_dict.get('program')
        instruction.program_id = json_dict.get('programId')

        if 'parsed' in json_dict:
            parsed = json_dict.get('parsed')
            if isinstance(parsed, dict):
                instruction.instruction_type = parsed.get('type')
                instruction.params = parsed.get('info')
            else:
                instruction.parsed = parsed

        return instruction

    def to_dict(self, instruction: Instruction) -> Dict:
        return {
            'type': 'instruction',
            'tx_signature': instruction.tx_signature,
            'index': instruction.index,
            'parent_index': instruction.parent_index,
            'accounts': json.dumps(instruction.accounts),
            'data': instruction.data,
            'program': instruction.program,
            'program_id': instruction.program_id,
            'instruction_type': instruction.instruction_type,
            'params': json.dumps(instruction.params),
        }

    def from_dict(self, dict: Dict) -> Instruction:
        instruction = Instruction()

        instruction.tx_signature = dict.get('tx_signature')
        instruction.index = dict.get('index')
        instruction.parent_index = dict.get('parent_index')
        instruction.accounts = json.loads(dict.get('accounts'))
        instruction.data = dict.get('data')
        instruction.program = dict.get('program')
        instruction.program_id = dict.get('program_id')
        instruction.instruction_type = dict.get('instruction_type')
        instruction.params = json.loads(dict.get('params'))

        return instruction
