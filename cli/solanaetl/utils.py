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


import contextlib
import csv
import json
import logging
from typing import List

from blockchainetl_common.csv_utils import set_max_field_size_limit
from blockchainetl_common.file_utils import get_file_handle, smart_open

from solanaetl.misc.retriable_value_error import RetriableValueError


def chunk(a, chunk_size):
    for i in range(0, len(a), chunk_size):
        yield a[i:i + chunk_size]


def hex_to_dec(hex_string):
    if hex_string is None:
        return None
    try:
        return int(hex_string, 16)
    except ValueError:
        print("Not a hex string %s" % hex_string)
        return hex_string


def to_normalized_address(address):
    if address is None or not isinstance(address, str):
        return address
    return address.lower()


def validate_range(range_start_incl, range_end_incl):
    if range_start_incl < 0 or range_end_incl < 0:
        raise ValueError(
            'range_start and range_end must be greater or equal to 0')

    if range_end_incl < range_start_incl:
        raise ValueError('range_end must be greater or equal to range_start')


def dynamic_batch_iterator(iterable, batch_size_getter):
    batch = []
    batch_size = batch_size_getter()
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
            batch_size = batch_size_getter()
    if len(batch) > 0:
        yield batch


def rpc_response_batch_to_results(response):
    for response_item in response:
        yield rpc_response_to_result(response_item)


def rpc_response_to_result(response):
    result = response.get('result')
    if result is None:
        error_message = 'result is None in response {}.'.format(response)
        if response.get('error') is None:
            error_message = error_message + ' Make sure node is synced.'
            # When nodes are behind a load balancer it makes sense to retry the request in hopes it will go to other,
            # synced node
            raise RetriableValueError(error_message)
        elif response.get('error') is not None and is_skipable_error(response.get('error').get('code')):
            logging.warning(error_message)
            return None
        elif response.get('error') is not None and is_retriable_error(response.get('error').get('code')):
            raise RetriableValueError(error_message)
        raise ValueError(error_message)
    return result


SKIPABLE_ERRORS = [
    -32009,  # Slot {} was skipped, or missing in long-term storage
]


def is_skipable_error(error_code):
    if error_code in SKIPABLE_ERRORS:
        return True


def is_retriable_error(error_code):
    if error_code is None:
        return False

    if not isinstance(error_code, int):
        return False

    # https://www.jsonrpc.org/specification#error_object
    if error_code == -32603 or (-32000 >= error_code >= -32099):
        return True

    return False


@contextlib.contextmanager
def get_item_iterable(input_file):
    fh = get_file_handle(input_file, 'r')

    if input_file.endswith('.csv'):
        set_max_field_size_limit()
        reader = csv.DictReader(fh)
    else:
        reader = (json.loads(line) for line in fh)

    try:
        yield reader
    finally:
        fh.close()


def extract_field(input_file, output_file, field):
    with get_item_iterable(input_file) as item_iterable, smart_open(output_file, 'w') as output:
        for item in item_iterable:
            output.write(item[field] + '\n')


def safe_get(arr: List, index: int, default=None):
    try:
        return arr[index]
    except:
        return default
