# -*- coding: utf-8 -*-

# Andy Sayler
# 2014, 2015
# University of Colorado


### Imports ###


### Constants ###

ENCODING = 'utf-8'


### Exceptions ###

class KeyvalError(Exception):
    """Base class for Keyval Exceptions"""

    def __init__(self, *args, **kwargs):
        super(KeyvalError, self).__init__(*args, **kwargs)

class PersistentError(KeyvalError):
    """Base class for Persistent Exceptions"""

    def __init__(self, *args, **kwargs):
        super(PersistentError, self).__init__(*args, **kwargs)

class ObjectExists(PersistentError):
    """Object Exists Exception"""

    def __init__(self, obj):
        msg = "{:s} already exists.".format(repr(obj))
        super(ObjectExists, self).__init__(msg)

class ObjectDNE(PersistentError):
    """Object Does Not Exist Exception"""

    def __init__(self, obj):
        msg = "{:s} does not exist.".format(repr(obj))
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
