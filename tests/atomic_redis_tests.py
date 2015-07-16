#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Andy Sayler
# Summer 2015
# Univerity of Colorado


### Imports ###

## stdlib ##
import unittest
import warnings

## keyval ##
import keyval.atomic_redis

## tests ##
import base_abc_tests
import base_redis_tests


### Globals ###

_REDIS_DB = 9


### Base Class ###

class RedisAtomicTestCase(base_redis_tests.RedisBaseTestCase):

    def __init__(self, *args, **kwargs):
        super(RedisAtomicTestCase, self).__init__(*args, **kwargs)
        self.module = keyval.atomic_redis
        self.driver = self.module.Driver(db=_REDIS_DB)


### Object Classes ###

class StringTestCase(base_abc_tests.StringMixin, RedisAtomicTestCase):
    pass

class MutableStringTestCase(base_abc_tests.MutableStringMixin, RedisAtomicTestCase):
    pass

class ListTestCase(base_abc_tests.ListMixin, RedisAtomicTestCase):
    pass

class MutableListTestCase(base_abc_tests.MutableListMixin, RedisAtomicTestCase):
    pass


### Main ###

if __name__ == '__main__':
    unittest.main()
