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


import pytest
import tests.resources
from solanaetl.jobs.export_instructions_job import ExportInstructionsJob
from solanaetl.jobs.exporters.instructions_item_exporter import \
    instructions_item_exporter
from solanaetl.thread_local_proxy import ThreadLocalProxy
from tests.helpers import (compare_lines_ignore_order, read_file,
                           skip_if_slow_tests_disabled)
from tests.solanaetl.job.helpers import get_web3_provider

RESOURCE_GROUP = 'test_export_instructions_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize(
    'transactions,resource_group,web3_provider_type',
    [
        (['21w7wVXW6ZdEkxv1zmZXJPnKXM57vwyDU8VLHwRrD5WTH9ZwgGGWhbQgmF563UAjY6MpG3fktmbs3uiREjXN7iw8'],
         'instructions_only', 'mock'),
        skip_if_slow_tests_disabled(
            (['21w7wVXW6ZdEkxv1zmZXJPnKXM57vwyDU8VLHwRrD5WTH9ZwgGGWhbQgmF563UAjY6MpG3fktmbs3uiREjXN7iw8'],
             'instructions_only', 'online'),
        )
    ],
)
def test_export_instructions(
    tmpdir, transactions, resource_group, web3_provider_type
):
    instructions_output_file = str(tmpdir.join('actual_instructions.csv'))

    job = ExportInstructionsJob(
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(
                web3_provider_type,
                lambda file: read_resource(resource_group, file),
                batch=True,
            )
        ),
        max_workers=5,
        item_exporter=instructions_item_exporter(
            instructions_output=instructions_output_file,
        ),
        transaction_addresses_iterable=transactions,
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_instructions.csv'),
        read_file(instructions_output_file),
    )
