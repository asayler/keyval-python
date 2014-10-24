#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado


import unittest

import redis

import keyval.base
import keyval.base_redis

import base_tests


class RedisBaseTestCase(base_tests.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(RedisBaseTestCase, self).__init__(*args, **kwargs)
        self.module = keyval.base_redis
        self.driver = keyval.base_redis.Driver()

    def setUp(self):
        super(RedisBaseTestCase, self).setUp()

    def tearDown(self):
        super(RedisBaseTestCase, self).tearDown()

class StringTestCase(base_tests.StringMixin, RedisBaseTestCase):

    pass

### Main ###
if __name__ == '__main__':
    unittest.main()
