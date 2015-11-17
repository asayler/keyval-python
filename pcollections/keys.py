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


### Key Types ###

class BaseKey(object):
    pass

class StrKey(BaseKey, str):

    def __init__(self, key):

        # Validate Key
        if not (isinstance(key, str) or isinstance(key, native_str)):
            raise TypeError("key must by a str()")

        # Call Parent
        super(StrKey, self).__init__()

    def get_key(self):
        return self
