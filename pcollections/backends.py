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

from . import drivers
from . import be_redis_base
from . import be_redis_atomic


### Abstract Classes ###

class Backend(with_metaclass(abc.ABCMeta, object)):

    ## Methods ##

    @abc.abstractmethod
    def __init__(self, module, driver):

        # Check Args
        if not isinstance(driver, drivers.Driver):
            raise TypeError("driver must be instance of Driver")

        # Call Parent
        super().__init__()

        # Save Attrs
        self._driver = driver
        self._module = module

    ## Properties ##

    @property
    def driver(self):
        return self._driver

    @property
    def module(self):
        return self._module


### Classes ###

class RedisBaseBackend(Backend):

    ## Methods ##

    def __init__(self, driver):

        # Check Input
        if not isinstance(driver, drivers.RedisDriver):
            raise TypeError("driver must be instance of RedisDriver")

        # Call Parent
        super().__init__(be_redis_base, driver)

class RedisAtomicBackend(Backend):

    ## Methods ##

    def __init__(self, driver):

        # Check Input
        if not isinstance(driver, drivers.RedisDriver):
            raise TypeError("driver must be instance of RedisDriver")

        # Call Parent
        super().__init__(be_redis_atomic, driver)
