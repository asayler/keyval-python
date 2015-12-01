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
from future.utils import with_metaclass
from builtins import *

import abc
import uuid


### Key Types ###

class BaseKey(with_metaclass(abc.ABCMeta, object)):

    @abc.abstractmethod
    def __init__(self, key):

        # Call Parent
        super(BaseKey, self).__init__()

        # Set Attrs
        self._key = key

    def __str__(self):
        """Return String Representation"""
        return str(self._key)

    def __repr__(self):
        """Return Unique Representation"""
        return self.key

    @property
    def key(self):
        return self._key

class StrKey(BaseKey):

    def __init__(self, key):

        # Validate Input
        if not (isinstance(key, str) or isinstance(key, native_str)):
            raise TypeError("key must by a str()")

        # Call Parent
        super(StrKey, self).__init__(key)

class UUIDKey(BaseKey):

    _SEPERATOR = "_"

    def __init__(self, uid, prefix=None, postfix=None):

        # Validate Input
        if not (isinstance(uid, uuid.UUID)):
            raise TypeError("uid must by a uuid.UUID(), not '{}'".format(type(uid)))
        if prefix is not None:
            if not (isinstance(prefix, str) or isinstance(prefix, native_str)):
                msg = "prefix must be type '{}', not '{}'".format(str, type(prefix))
                raise TypeError(msg)
        if postfix is not None:
            if not (isinstance(postfix, str) or isinstance(postfix, native_str)):
                msg = "postfix must be type '{}', not '{}'".format(str, type(postfix))
                raise TypeError(msg)

        # Setup Key
        key = str()
        if prefix:
            key += (str(prefix) + _SEPERATOR)
        key += str(uid)
        if postfix:
            key += (_SEPERATOR + str(postixfix))

        # Call Parent
        super(UUIDKey, self).__init__(key)

        # Set Attrs
        self._uid = uid

    @property
    def uid(self):
        return self._uid
