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
from future.utils import native_str
from builtins import *

standard_library.install_aliases()


### Factories ###

class InstanceFactory(object):

    def __init__(self, driver, obj):

        # Call Parent
        super(InstanceFactory, self).__init__()

        # Save Attrs
        self.driver = driver
        self.obj = obj

    def from_new(self, key, val, *args, **kwargs):
        return self.obj.from_new(self.driver, key, val, *args, **kwargs)

    def from_existing(self, key, *args, **kwargs):
        return self.obj.from_existing(self.driver, key, *args, **kwargs)

    def from_raw(self, key, *args, **kwargs):
        return self.obj.from_raw(self.driver, key, *args, **kwargs)
