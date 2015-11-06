## -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015
# pcollections Package


### Exceptions ###

class PcollectionsError(Exception):
    """Base class for pcollections Exceptions"""

    def __init__(self, *args, **kwargs):
        super(PcollectionsError, self).__init__(*args, **kwargs)

class PersistentError(PcollectionsError):
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
