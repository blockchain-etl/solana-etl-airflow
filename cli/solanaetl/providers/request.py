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


import logging

import lru
import requests
from requests.adapters import HTTPAdapter
from web3._utils.caching import generate_cache_key


def _remove_session(key, session):
    session.close()


_session_cache = lru.LRU(8, callback=_remove_session)


MAX_POOL_SIZE = 40


def _get_session(*args, **kwargs) -> requests.Session:
    cache_key = generate_cache_key((args, kwargs))
    if cache_key not in _session_cache:
        session = requests.Session()
        session.mount('https://', HTTPAdapter(pool_maxsize=MAX_POOL_SIZE))
        session.mount('http://', HTTPAdapter(pool_maxsize=MAX_POOL_SIZE))
        _session_cache[cache_key] = session
    return _session_cache[cache_key]


def make_post_request(endpoint_uri, data, *args, **kwargs):
    kwargs.setdefault('timeout', 10)
    session = _get_session(endpoint_uri)
    response = session.post(endpoint_uri, data=data, *args, **kwargs)
    try:
        response.raise_for_status()
    except Exception as e:
        logging.error(
            'Exception occurred while making a post request, response body was: ' + (response.text or ''))
        raise e

    return response.content
