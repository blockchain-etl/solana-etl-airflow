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


from typing import Any, Callable, List, Tuple

from base58 import b58encode

V2E32 = pow(2, 32)


def rounded_int64(hi32, lo32):
    return hi32 * V2E32 + lo32


def sint(data: bytes, n_bytes: int, offset: int = 0) -> Tuple[int, int]:
    """signed int"""
    data_bytes, offset = blob(data, n_bytes, offset)
    return int.from_bytes(data_bytes, byteorder="little", signed=True), offset


def uint(data: bytes, n_bytes: int, offset: int = 0) -> Tuple[int, int]:
    """unsigned int"""
    data_bytes, offset = blob(data, n_bytes, offset)
    return int.from_bytes(data_bytes, byteorder="little"), offset


def u8(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return uint(data, 1, offset)


def u16(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return uint(data, 2, offset)


def u32(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return uint(data, 4, offset)


def u64(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return uint(data, 8, offset)


def u128(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return uint(data, 16, offset)


def ns64(data: bytes, offset: int = 0) -> Tuple[int, int]:
    lo32, next_offset = u32(data, offset)
    hi32, next_offset = u32(data, next_offset)
    return rounded_int64(hi32, lo32), next_offset


def blob(data: bytes, n_bytes: int, offset: int = 0) -> Tuple[bytes, int]:
    return data[offset:offset+n_bytes], offset+n_bytes


def public_key(data: bytes, offset: int = 0) -> Tuple[str, int]:
    public_key_bytes, next_offset = blob(data, 32, offset)
    return b58encode(public_key_bytes).decode("utf-8"), next_offset


def iter_blob(data: bytes, item_handler: Callable, n_items: int, offset: int = 0) -> Tuple[List, int]:
    results = []
    next_offset = offset
    for i in range(n_items):
        decoded_data, next_offset = item_handler(data, next_offset)
        results.append(decoded_data)

    return results, next_offset
