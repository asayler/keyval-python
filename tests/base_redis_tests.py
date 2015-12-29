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
import warnings

## pcollections ##
from pcollections import drivers
from pcollections import backends
from pcollections import collections

## tests ##
import test_mixins


### Globals ###

_REDIS_DB = 9


### Exceptions ###

class RedisBaseTestError(test_mixins.BaseTestError):
    """Base class for RedisBaseTest Exceptions"""

    pass

class RedisDatabaseNotEmpty(RedisBaseTestError):

    def __init__(self, redis):
        msg = "Redis DB not empty: {:d} keys".format(redis.dbsize())
        super(RedisDatabaseNotEmpty, self).__init__(msg)


### Base Class ###

class RedisBaseTestCase(test_mixins.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(RedisBaseTestCase, self).__init__(*args, **kwargs)
        self.driver = drivers.RedisDriver(db=_REDIS_DB)
        self.backend = backends.RedisBaseBackend(self.driver)
        self.collection = collections.PCollections(self.backend)

    def setUp(self):

        # Call Parent
        super(RedisBaseTestCase, self).setUp()

        # Confirm Empty DB
        if (self.driver.redis.dbsize() != 0):
            raise RedisDatabaseNotEmpty(self.driver.redis)

    def tearDown(self):

        # Confirm Empty DB
        if (self.driver.redis.dbsize() != 0):
            print("")
            warnings.warn("Redis database not empty prior to tearDown")
            self.driver.redis.flushdb()

        # Call Parent
        super(RedisBaseTestCase, self).tearDown()


### Object Classes ###

class StringTestCase(test_mixins.StringMixin, RedisBaseTestCase):
    pass

class MutableStringTestCase(test_mixins.MutableStringMixin, RedisBaseTestCase):
    pass

class ListTestCase(test_mixins.ListMixin, RedisBaseTestCase):
    pass

class MutableListTestCase(test_mixins.MutableListMixin, RedisBaseTestCase):
    pass

class SetTestCase(test_mixins.SetMixin, RedisBaseTestCase):
    pass

class MutableSetTestCase(test_mixins.MutableSetMixin, RedisBaseTestCase):
    pass

class DictionaryTestCase(test_mixins.DictionaryMixin, RedisBaseTestCase):
    pass

class MutableDictionaryTestCase(test_mixins.MutableDictionaryMixin, RedisBaseTestCase):
    pass
