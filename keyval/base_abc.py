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

class PersistentObject(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(PersistentObject, self).__init__()

        # Save Attrs
        self._driver = driver
        self._key = str(key)

    @abstractclassmethod
    def from_new(cls, driver, key, *args, **kwargs):
        """New Constructor"""

        # Get Object
        obj = cls.from_raw(driver, key, *args, **kwargs)

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
        return unicode(self.val())

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

    def key(self):
        """Get Key"""
        return self._key

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

class SequenceObject(collections.Sequence, PersistentObject):

    def __len__(self):
        """Get Len of Set"""
        return len(self.val())

    def __getitem__(self, key):
        """Get Item"""
        return self.val()[key]

    def __contains__(self, item):
        """Contains Item"""
        return item in self.val()

    def __iter__(self):
        """Iterate Across Val"""
        for i in self.val():
            yield i

### Abstract Objects ###

class String(SequenceObject):

    pass
