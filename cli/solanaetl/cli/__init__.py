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

import click
from solanaetl.cli.export_all import export_all
from solanaetl.cli.export_blocks_and_transactions import export_blocks_and_transactions
from solanaetl.cli.export_instructions import export_instructions
from solanaetl.cli.extract_accounts import extract_accounts
from solanaetl.cli.extract_field import extract_field
from solanaetl.cli.extract_token_transfers import extract_token_transfers
from solanaetl.cli.extract_tokens import extract_tokens


@click.group()
@click.version_option(version="0.0.1")
@click.pass_context
def cli(ctx):
    pass


# export
cli.add_command(export_all, "export_all")
cli.add_command(export_blocks_and_transactions, "export_blocks_and_transactions")
cli.add_command(export_instructions, "export_instructions")

# extract
cli.add_command(extract_token_transfers, "extract_token_transfers")
cli.add_command(extract_accounts, "extract_accounts")
cli.add_command(extract_tokens, "extract_tokens")

# utils
cli.add_command(extract_field, "extract_field")
