#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Andy Sayler
# Summer 2014
# Univerity of Colorado


### Imports ###

## stdlib ##
import unittest
import warnings

## keyval ##
import keyval.base
import keyval.base_redis

## tests ##
import base_tests


### Globals ###

_REDIS_DB = 9


### Exceptions ###

class RedisBaseTestError(base_tests.BaseTestError):
    """Base class for RedisBaseTest Exceptions"""

    def __init__(self, *args, **kwargs):
        super(RedisBaseTestError, self).__init__(*args, **kwargs)

class RedisDatabaseNotEmpty(RedisBaseTestError):

    def __init__(self, driver):
        msg = "Redis DB not empty: {:d} keys".format(driver.dbsize())
        super(RedisDatabaseNotEmpty, self).__init__(msg)


### Base Class ###

class RedisBaseTestCase(base_tests.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(RedisBaseTestCase, self).__init__(*args, **kwargs)
        self.module = keyval.base_redis
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

class StringTestCase(base_tests.StringMixin, RedisBaseTestCase):
    pass

class MutableStringTestCase(base_tests.MutableStringMixin, RedisBaseTestCase):
    pass

class ListTestCase(base_tests.ListMixin, RedisBaseTestCase):
    pass

class MutableListTestCase(base_tests.MutableListMixin, RedisBaseTestCase):
    pass

class SetTestCase(base_tests.SetMixin, RedisBaseTestCase):
    pass

class MutableSetTestCase(base_tests.MutableSetMixin, RedisBaseTestCase):
    pass

class MappingTestCase(base_tests.MappingMixin, RedisBaseTestCase):
    pass

class MutableMappingTestCase(base_tests.MutableMappingMixin, RedisBaseTestCase):
    pass


### Main ###

if __name__ == '__main__':
    unittest.main()
