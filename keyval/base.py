# -*- coding: utf-8 -*-

# Andy Sayler
# Fall 2014
# Univerity of Colorado


import uuid
import collections
import time
import copy


_ENCODING = 'utf-8'
_SEP_FIELD = ':'


### Exceptions ###

class KeyvalError(Exception):
    """Base class for Keyval Exceptions"""

    def __init__(self, *args, **kwargs):
        super(KeyvalError, self).__init__(*args, **kwargs)

class PersistentObjectError(KeyvalError):
    """Base class for PersistentObject Exceptions"""

    def __init__(self, *args, **kwargs):
        super(PersistentObjectError, self).__init__(*args, **kwargs)

class ObjectExists(PersistentObjectError):
    """Object Exists Exception"""

    def __init__(self, obj):
        msg = "{:s} already exists.".format(obj)
        super(ObjectExists, self).__init__(msg)

class ObjectDNE(PersistentObjectError):
    """Object Does Not Exist Exception"""

    def __init__(self, obj):
        msg = "{:s} does not exist.".format(obj)
        super(ObjectDNE, self).__init__(msg)


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
