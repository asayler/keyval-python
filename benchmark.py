#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015, 2016
# pcollections Tests

### Imports ###

## Future ##
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.utils import native_str
from builtins import *

## stdlib ##
import time

## pcollections ##
from pcollections import drivers
from pcollections import backends
from pcollections import collections

_REDIS_DB = 9
_ITR = 100000

if __name__ == '__main__':

    # Setup Connection
    driver = drivers.RedisDriver(db=_REDIS_DB)
    backend = backends.RedisBaseBackend(driver)
    collections = collections.PCollections(backend)

    itr = _ITR

    # Confirm Empty DB
    if (driver.redis.dbsize() != 0):
        raise Exception("DB Not Empty")

    print("Testing Native String Read...")
    s = str("Test String 1..2..3..")
    start = time.perf_counter()
    for i in range(itr):
        val = str(s)
    end = time.perf_counter()
    dur = end - start
    iops = itr/dur
    print("iops ({} iterations) = {}".format(itr, iops))

    print("Testing Collections String Read...")
    s = collections.String("test_string", create="Test String 1..2..3..")
    start = time.perf_counter()
    for i in range(itr):
        val = str(s)
    end = time.perf_counter()
    dur = end - start
    iops = itr/dur
    print("iops ({} iterations) = {}".format(itr, iops))

    # Clear DB
    driver.redis.flushdb()
