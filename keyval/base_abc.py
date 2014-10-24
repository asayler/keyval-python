# -*- coding: utf-8 -*-

# Andy Sayler
# Fall 2014
# Univerity of Colorado


import abc
import uuid
import collections
import time
import copy

import base


_ENCODING = 'utf-8'
_SEP_FIELD = ':'
_SEP_TYPE = '+'


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

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(PersistentObject, self).__init__()

        # Save Attrs
        self.driver = driver
        self.key = str(key)

    def __unicode__(self):
        """Return Unicode Representation"""
        return unicode(self.val())

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
        return (self.val() == other.val())

    @abstractclassmethod
    def from_new(cls, driver, key, *args, **kwargs):
        """New Constructor"""
        return cls(driver, key, *args, **kwargs)

    @abstractclassmethod
    def from_existing(cls, driver, key, *args, **kwargs):
        """Existing Constructor"""
        return cls(driver, key, *args, **kwargs)

    @classmethod
    def from_raw(cls, driver, key, *args, **kwargs):
        """Raw Constructor"""
        return cls(driver, key, *args, **kwargs)

    def key(self):
        """Get Key"""
        return self.key

    @abc.abstractmethod
    def val(self):
        """Get Value as Corresponding Python Object"""
        pass

    @abc.abstractmethod
    def rem(self):
        """Delete Object"""
        pass

    @abc.abstractmethod
    def exists(self):
        """Check if Object Exists"""
        pass


class String(collections.Sequence, PersistentObject):

    @abc.abstractmethod
    def __len__(self):
        """Get Len of Set"""
        pass

    @abc.abstractmethod
    def __getitem__(self):
        """Iterate Values"""
        pass
