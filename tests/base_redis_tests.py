#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Andy Sayler


### Imports ###

## stdlib ##
import unittest
import warnings

## pcollections ##
import pcollections.base_redis

## tests ##
import test_mixins


### Globals ###

_REDIS_DB = 9


### Exceptions ###

class RedisBaseTestError(test_mixins.BaseTestError):
    """Base class for RedisBaseTest Exceptions"""

    pass

class RedisDatabaseNotEmpty(RedisBaseTestError):

    def __init__(self, driver):
        msg = "Redis DB not empty: {:d} keys".format(driver.dbsize())
        super(RedisDatabaseNotEmpty, self).__init__(msg)


### Base Class ###

class RedisBaseTestCase(test_mixins.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(RedisBaseTestCase, self).__init__(*args, **kwargs)
        self.module = pcollections.base_redis
        self.driver = self.module.Driver(db=_REDIS_DB)

    def setUp(self):

        # Call Parent
        super(RedisBaseTestCase, self).setUp()

        # Confirm Empty DB
        if (self.driver.dbsize() != 0):
            raise RedisDatabaseNotEmpty(self.driver)

    def tearDown(self):

        # Confirm Empty DB
        if (self.driver.dbsize() != 0):
            warnings.warn("Redis database not empty prior to tearDown")
            self.driver.flushdb()

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


### Main ###

if __name__ == '__main__':
    unittest.main()
