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


import csv
import io

import pytest
from solanaetl.jobs.exporters.token_transfers_item_exporter import token_transfers_item_exporter
from solanaetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
import tests.resources
from blockchainetl_common.csv_utils import set_max_field_size_limit
from solanaetl.jobs.exporters.tokens_item_exporter import tokens_item_exporter
from solanaetl.jobs.extract_tokens_job import ExtractTokensJob
from solanaetl.thread_local_proxy import ThreadLocalProxy
from tests.helpers import (compare_lines_ignore_order, read_file,
                           skip_if_slow_tests_disabled)
from tests.solanaetl.job.helpers import get_web3_provider

RESOURCE_GROUP = 'test_extract_token_transfers_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize(
    'batch_size,resource_group',
    [
        (100, 'token_transfers_only'),
    ],
)
def test_extract_token_transfers(
    tmpdir, batch_size, resource_group
):
    token_transfers_output_file = str(
        tmpdir.join('actual_token_transfers.csv'))

    instructions_content = read_resource(resource_group, 'instructions.csv')
    set_max_field_size_limit()
    instructions_csv_reader = csv.DictReader(io.StringIO(instructions_content))

    job = ExtractTokenTransfersJob(
        batch_size=batch_size,
        max_workers=5,
        item_exporter=token_transfers_item_exporter(
            token_transfers_output=token_transfers_output_file,
        ),
        instructions_iterable=instructions_csv_reader,
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_token_transfers.csv'),
        read_file(token_transfers_output_file),
    )
