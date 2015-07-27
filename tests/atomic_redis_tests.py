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
import test_mixins
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

class StringTestCase(test_mixins.StringMixin, RedisAtomicTestCase):
    pass

class MutableStringTestCase(test_mixins.MutableStringMixin, RedisAtomicTestCase):
    pass

class ListTestCase(test_mixins.ListMixin, RedisAtomicTestCase):
    pass

class MutableListTestCase(test_mixins.MutableListMixin, RedisAtomicTestCase):
    pass

class SetTestCase(test_mixins.SetMixin, RedisAtomicTestCase):
    pass

class MutableSetTestCase(test_mixins.MutableSetMixin, RedisAtomicTestCase):
    pass

class DictionaryTestCase(test_mixins.DictionaryMixin, RedisAtomicTestCase):
    pass

class MutableDictionaryTestCase(test_mixins.MutableDictionaryMixin, RedisAtomicTestCase):
    pass


### Main ###

if __name__ == '__main__':
    unittest.main()
