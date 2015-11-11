# -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015
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
import unittest

## keyval ##
import pcollections.be_redis_atomic

## tests ##
import test_mixins
import base_redis_tests


### Globals ###

_REDIS_DB = 9


### Base Class ###

class RedisAtomicTestCase(base_redis_tests.RedisBaseTestCase):

    def __init__(self, *args, **kwargs):
        super(RedisAtomicTestCase, self).__init__(*args, **kwargs)
        self.module = pcollections.be_redis_atomic
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
