## -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015
# pcollections Package


### Imports ###

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from future.utils import native_str
from builtins import *

from . import keys

### Factories ###

class InstanceFactory(object):

    def __init__(self, driver, obj_type, key_type=keys.StrKey, key_kwargs={}):

        # Call Parent
        super(InstanceFactory, self).__init__()

        # Save Attrs
        self._driver = driver
        self._key_type = key_type
        self._key_kwargs = key_kwargs
        self._obj_type = obj_type

    def from_new(self, key, val, *args, **kwargs):
        key = self._key_type(key, **self._key_kwargs)
        return self._obj_type.from_new(self._driver, key, val, *args, **kwargs)

    def from_existing(self, key, *args, **kwargs):
        key = self._key_type(key, **self._key_kwargs)
        return self._obj_type.from_existing(self._driver, key, *args, **kwargs)

    def from_raw(self, key, *args, **kwargs):
        key = self._key_type(key, **self._key_kwargs)
        return self._obj_type.from_raw(self._driver, key, *args, **kwargs)
