# -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015
# pcollections Package


### Pylint ###


### Imports ###

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from future.utils import native_str
from future.utils import with_metaclass
from future.utils import python_2_unicode_compatible
from builtins import *

import abc

import redis


### Abstract Classes ###

class Driver(with_metaclass(abc.ABCMeta, object)):

    pass


### Classes ###

class RedisDriver(Driver):

    def __init__(self, *args, **kwargs):

        self._redis = redis.StrictRedis(*args, **kwargs)

        # Call Parent
        super().__init__()

    @property
    def redis(self):
        return self._redis
