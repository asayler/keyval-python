# -*- coding: utf-8 -*-

# Andy Sayler
# Fall 2014
# Univerity of Colorado


import abc
import uuid
import collections
import time
import copy

_ENCODING = 'utf-8'
_SEP_FIELD = ':'
_SEP_TYPE = '+'


### Exceptions ###

class KeyvalError(Exception):
    """Base class for Keyval Exceptions"""

    def __init__(self, *args, **kwargs):
        super(Keyval, self).__init__(*args, **kwargs)


### Helpers ###

class abstractstaticmethod(staticmethod):
    __slots__ = ()
    def __init__(self, function):
        super(abstractstaticmethod, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True


class abstractclassmethod(classmethod):
    __slots__ = ()
    def __init__(self, function):
        super(abstractclassmethod, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True


### Abstract Base Objects ###

class PersistentObject(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, key):
        """ Constructor"""

        # Call Parent
        super(PersistentObject, self).__init__()

        # Save Attrs
        self.key = str(key)

    def __unicode__(self):
        """Return Unicode Representation"""
        return unicode(repr(self))

    def __str__(self):
        """Return String Representation"""
        return unicode(self).encode(_ENCODING)

    def __repr__(self):
        """Return Unique Representation"""
        return self.key

    def __hash__(self):
        """Return Hash"""
        return hash(repr(self))

    def __eq__(self, other):
        """Test Equality"""
        return (repr(self) == repr(other))

    @abstractclassmethod
    def from_new(cls, *args, **kwargs):
        """New Constructor"""
        return cls(*args, **kwargs)

    @abstractclassmethod
    def from_existing(cls, *args, **kwargs):
        """Existing Constructor"""
        return cls(*args, **kwargs)

    @abstractclassmethod
    def from_raw(cls, *args, **kwargs):
        """Raw Constructor"""
        return cls(*args, **kwargs)

    @abc.abstractmethod
    def delete(self):
        """Delete Object"""
        pass

    @abc.abstractmethod
    def exists(self):
        """Check if Object Exists"""
        pass


class StringObject(collections.Sequence, PersistentObject):

    @abc.abstractmethod
    def __len__(self):
        """Get Len of Set"""
        pass

    @abc.abstractmethod
    def __getitem__(self):
        """Iterate Values"""
        pass
