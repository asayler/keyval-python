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

class Persistent(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(Persistent, self).__init__()

        # Save Attrs
        self._driver = driver
        self._key = str(key)

    @classmethod
    def from_new(cls, driver, key, val, *args, **kwargs):
        """New Constructor"""

        # Get Object
        obj = cls.from_raw(driver, key, *args, **kwargs)

        # Create New Object
        obj._set_val(val, create=True, overwrite=False)

        # Return Object
        return obj

    @classmethod
    def from_existing(cls, driver, key, *args, **kwargs):
        """Existing Constructor"""

        # Get Object
        obj = cls.from_raw(driver, key, *args, **kwargs)

        # Check Existence
        if not obj.exists():
            raise base.ObjectDNE(obj)

        # Return Object
        return obj

    @classmethod
    def from_raw(cls, driver, key, *args, **kwargs):
        """Raw Constructor"""
        return cls(driver, key, *args, **kwargs)

    def __unicode__(self):
        """Return Unicode Representation"""
        return unicode(self.get_val())

    def __str__(self):
        """Return String Representation"""
        return unicode(self).encode(base._ENCODING)

    def __repr__(self):
        """Return Unique Representation"""
        return self.key()

    def __hash__(self):
        """Return Hash"""
        return hash(self.key())

    def __nonzero__(self):
        """Test Bool"""
        return self.exists()

    def __eq__(self, other):
        """Test Equality"""
        if (type(self) == type(other)):
            return (self.key() == other.key())
        else:
            return False

    def __ne__(self, other):
        """Test Unequality"""
        if (type(self) == type(other)):
            return (self.key() != other.key())
        else:
            return True

    @abc.abstractmethod
    def _get_val(self):
        """Get Value"""
        pass

    @abc.abstractmethod
    def _set_val(self, val, create=True, overwrite=True):
        """Set Value"""
        pass

    def key(self):
        """Get Key"""
        return self._key

    def get_val(self):
        """Get Value as Corresponding Python Object"""
        return self._get_val()

    @abc.abstractmethod
    def rem(self, force=False):
        """Delete Object"""
        pass

    @abc.abstractmethod
    def exists(self):
        """Check if Object Exists"""
        pass

class Mutable(Persistent):

    def set_val(self, val):
        """Set Value of Persistent Object"""
        return self._set_val(val, create=False, overwrite=True)

class Sequence(collections.Sequence, Persistent):

    def __len__(self):
        """Get Len of Set"""
        return len(self.get_val())

    def __getitem__(self, i):
        """Get Seq Item"""
        return self.get_val()[i]

    def __contains__(self, i):
        """Contains Seq Item"""
        return i in self.get_val()

    def __iter__(self):
        """Iterate Across Seq"""
        for i in self.get_val():
            yield i

class MutableSequence(collections.MutableSequence, Sequence, Mutable):

    @abc.abstractmethod
    def __setitem__(self, i, val):
        """Set Seq Item"""
        pass

    @abc.abstractmethod
    def __delitem__(self, i):
        """Del Seq Item"""
        pass

    @abc.abstractmethod
    def insert(self, i, x):
        """Insert Seq Item"""
        pass


### Abstract Objects ###

class String(Sequence):

    pass

class MutableString(MutableSequence, String):

    pass
