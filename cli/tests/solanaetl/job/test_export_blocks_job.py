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
from solanaetl.jobs.export_blocks_job import ExportBlocksJob
from solanaetl.jobs.exporters.blocks_and_transactions_item_exporter import \
    blocks_and_transactions_item_exporter
from solanaetl.thread_local_proxy import ThreadLocalProxy
from tests.helpers import (compare_lines_ignore_order, read_file,
                           skip_if_slow_tests_disabled)
from tests.solanaetl.job.helpers import get_web3_provider

RESOURCE_GROUP = 'test_export_blocks_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize(
    'start_block,end_block,batch_size,resource_group,web3_provider_type',
    [
        (138802069, 138802069, 1, 'blocks_only', 'mock'),
        skip_if_slow_tests_disabled(
            (138802069, 138802069, 1, 'blocks_only', 'online'),
        )
    ],
)
def test_export_blocks_job_blocks_only(
    tmpdir, start_block, end_block, batch_size, resource_group, web3_provider_type
):
    blocks_output_file = str(tmpdir.join('actual_blocks.csv'))

    job = ExportBlocksJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(
                web3_provider_type,
                lambda file: read_resource(resource_group, file),
                batch=True,
            )
        ),
        max_workers=5,
        item_exporter=blocks_and_transactions_item_exporter(
            blocks_output=blocks_output_file,
        ),
        export_blocks=blocks_output_file is not None,
        export_transactions=False,
        export_instructions=False,
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_blocks.csv'),
        read_file(blocks_output_file),
    )


@pytest.mark.parametrize(
    'start_block,end_block,batch_size,resource_group,web3_provider_type',
    [
        (138802069, 138802069, 1, 'blocks_with_transactions', 'mock'),
        skip_if_slow_tests_disabled(
            (138802069, 138802069, 1, 'blocks_with_transactions', 'online'),
        )
    ],
)
def test_export_blocks_job_with_transactions(
    tmpdir, start_block, end_block, batch_size, resource_group, web3_provider_type
):
    blocks_output_file = str(tmpdir.join('actual_blocks.csv'))
    transactions_output_file = str(tmpdir.join('actual_transactions.csv'))

    job = ExportBlocksJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(
                web3_provider_type,
                lambda file: read_resource(resource_group, file),
                batch=True,
            )
        ),
        max_workers=5,
        item_exporter=blocks_and_transactions_item_exporter(
            blocks_output=blocks_output_file,
            transactions_output=transactions_output_file,
        ),
        export_blocks=blocks_output_file is not None,
        export_transactions=transactions_output_file is not None,
        export_instructions=False,
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_blocks.csv'),
        read_file(blocks_output_file),
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_transactions.csv'),
        read_file(transactions_output_file),
    )


@pytest.mark.parametrize(
    'start_block,end_block,batch_size,resource_group,web3_provider_type',
    [
        (138802069, 138802069, 1, 'blocks_with_transactions_and_instructions', 'mock'),
        skip_if_slow_tests_disabled(
            (138802069, 138802069, 1,
             'blocks_with_transactions_and_instructions', 'online'),
        )
    ],
)
def test_export_blocks_job_with_transactions_and_instructions(
    tmpdir, start_block, end_block, batch_size, resource_group, web3_provider_type
):
    blocks_output_file = str(tmpdir.join('actual_blocks.csv'))
    transactions_output_file = str(tmpdir.join('actual_transactions.csv'))
    instructions_output_file = str(tmpdir.join('actual_instructions.csv'))

    job = ExportBlocksJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(
                web3_provider_type,
                lambda file: read_resource(resource_group, file),
                batch=True,
            )
        ),
        max_workers=5,
        item_exporter=blocks_and_transactions_item_exporter(
            blocks_output=blocks_output_file,
            transactions_output=transactions_output_file,
            instructions_output=instructions_output_file,
        ),
        export_blocks=blocks_output_file is not None,
        export_transactions=transactions_output_file is not None,
        export_instructions=instructions_output_file is not None,
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_blocks.csv'),
        read_file(blocks_output_file),
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_transactions.csv'),
        read_file(transactions_output_file),
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_instructions.csv'),
        read_file(instructions_output_file),
    )
