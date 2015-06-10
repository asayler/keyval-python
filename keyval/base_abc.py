# -*- coding: utf-8 -*-

# Andy Sayler
# Fall 2014
# Univerity of Colorado


import abc
import collections

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
        """Object Constructor"""

        # Check Input
        if driver is None:
            raise TypeError("driver must not be None")
        if key is None:
            raise TypeError("key must not be None")
        key = str(key)

        # Call Parent
        super(Persistent, self).__init__()

        # Save Attrs
        self._driver = driver
        self._key = key

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

    @abc.abstractmethod
    def _get_val(self):
        """Get Value"""
        pass

    @abc.abstractmethod
    def _set_val(self, val, create=False, overwrite=True):
        """Set Value"""
        pass

    @abc.abstractmethod
    def exists(self):
        """Check if Object Exists"""
        pass

    @abc.abstractmethod
    def rem(self, force=False):
        """Delete Object"""
        pass

    def __unicode__(self):
        """Return Unicode Representation"""
        return unicode(self.get_val())

    def __str__(self):
        """Return String Representation"""
        return unicode(self).encode(base._ENCODING)

    def __repr__(self):
        """Return Unique Representation"""
        return self.get_key()

    def __nonzero__(self):
        """Test Bool"""
        return bool(self.get_val())

    def get_key(self):
        """Get Key"""
        return self._key

    def get_val(self):
        """Get Value as Corresponding Python Object"""
        return self._get_val()

    def __eq__(self, other):
        """Test Equality"""
        if (type(other) == type(self)):
            return (self.get_val() == other.get_val())
        else:
            raise TypeError("Can only compare {}".format(type(self)))

    def __ne__(self, other):
        """Test Unequality"""
        if (type(other) == type(self)):
            return (self.get_val() != other.get_val())
        else:
            raise TypeError("Can only compare {}".format(type(self)))

    def __lt__(self, other):
        """Test Less Than"""
        if (type(other) == type(self)):
            return (self.get_val() < other.get_val())
        else:
            raise TypeError("Can only compare {}".format(type(self)))

    def __le__(self, other):
        """Test Less Than Equal"""
        if (type(other) == type(self)):
            return (self.get_val() <= other.get_val())
        else:
            raise TypeError("Can only compare {}".format(type(self)))

    def __gt__(self, other):
        """Test Greater Than"""
        if (type(other) == type(self)):
            return (self.get_val() > other.get_val())
        else:
            raise TypeError("Can only compare {}".format(type(self)))

    def __ge__(self, other):
        """Test Greater Than Equal"""
        if (type(other) == type(self)):
            return (self.get_val() >= other.get_val())
        else:
            raise TypeError("Can only compare {}".format(type(self)))

class Mutable(Persistent):

    def set_val(self, val):
        """Set Value of Persistent Object"""
        return self._set_val(val, create=False, overwrite=True)

class Container(Persistent, collections.Container):

    def __contains__(self, itm):
        """Contains Seq Item"""
        return itm in self.get_val()

class Iterable(Persistent, collections.Iterable):

    def __iter__(self):
        """Iterate Across Seq"""
        for itm in self.get_val():
            yield itm

class Sized(Persistent, collections.Sized):

    def __len__(self):
        """Get Len of Set"""
        return len(self.get_val())

class Sequence(Container, Iterable, Sized, collections.Sequence):

    def __getitem__(self, idx):
        """Get Seq Item"""
        return self.get_val()[idx]

    def __reversed__(self):
        """Iterate Backwards Across Seq"""
        for itm in reversed(self.get_val()):
            yield itm

    def index(self, itm):
        """Return index of first occurance of v"""
        return self.get_val().index(itm)

    def count(self, itm):
        """Return number os occurances of v"""
        return self.get_val().count(itm)

class MutableSequence(Mutable, Sequence, collections.MutableSequence):

    @abc.abstractmethod
    def __setitem__(self, idx, itm):
        """Set Seq Item"""
        pass

    @abc.abstractmethod
    def insert(self, idx, itm):
        """Insert Seq Item"""
        pass

    @abc.abstractmethod
    def append(self, itm):
        """Append Seq Item"""
        pass

    @abc.abstractmethod
    def extend(self, seq):
        """Extend Seq with another Seq"""
        pass

    @abc.abstractmethod
    def reverse(self):
        """Reverse Seq"""
        pass

    @abc.abstractmethod
    def pop(self, pop_idx=None):
        """Remove and return item"""
        pass

    @abc.abstractmethod
    def remove(self, itm):
        """Remove itm from seq"""
        pass

    @abc.abstractmethod
    def remove(self, itm):
        """Remove itm from seq"""
        pass

    def __iadd__(self, other):
        """+="""
        self.extend(other)

    def __delitem__(self, idx):
        """Del Seq Item"""
        self.pop(idx)


### Abstract Objects ###

class String(Sequence):
    pass

class MutableString(MutableSequence, String):
    pass

class List(Sequence):
    pass

class MutableList(MutableSequence, List):
    pass

class Set(Container, Iterable, Sized, collections.Set):

    def issubset(self, other):
        """Test Subset"""
        if (type(other) == type(self)):
            return (self.get_val().issubset(other.get_val()))
        else:
            raise TypeError("Can only compare {}".format(type(self)))

    def issuperset(self, other):
        """Test Superset"""
        if (type(other) == type(self)):
            return (self.get_val().issuperset(other.get_val()))
        else:
            raise TypeError("Can only compare {}".format(type(self)))

    def __and__(self, other):
        """Return Intersection"""
        if (type(other) == type(self)):
            return (self.get_val() & other.get_val())
        else:
            raise TypeError("Can only and {}".format(type(self)))

    def intersection(self, other):
        """Return Intersection"""
        if (type(other) == type(self)):
            return (self.get_val().intersection(other.get_val()))
        else:
            raise TypeError("Can only intersect {}".format(type(self)))

    def __or__(self, other):
        """Return Union"""
        if (type(other) == type(self)):
            return (self.get_val() | other.get_val())
        else:
            raise TypeError("Can only or {}".format(type(self)))

    def union(self, other):
        """Return Union"""
        if (type(other) == type(self)):
            return (self.get_val().union(other.get_val()))
        else:
            raise TypeError("Can only union {}".format(type(self)))

    def __sub__(self, other):
        """Return Difference"""
        if (type(other) == type(self)):
            return (self.get_val() - other.get_val())
        else:
            raise TypeError("Can only sub {}".format(type(self)))

    def difference(self, other):
        """Return Difference"""
        if (type(other) == type(self)):
            return (self.get_val().difference(other.get_val()))
        else:
            raise TypeError("Can only difference {}".format(type(self)))

    def __xor__(self, other):
        """Return Symmetric Difference"""
        if (type(other) == type(self)):
            return (self.get_val() ^ other.get_val())
        else:
            raise TypeError("Can only xor {}".format(type(self)))

    def symmetric_difference(self, other):
        """Return Symmetric Difference"""
        if (type(other) == type(self)):
            return (self.get_val().symmetric_difference(other.get_val()))
        else:
            raise TypeError("Can only symmetric_difference {}".format(type(self)))

    def isdisjoint(self, other):
        """Test Disjoint"""
        if (type(other) == type(self)):
            return (self.get_val().isdisjoint(other.get_val()))
        else:
            raise TypeError("Can only compare {}".format(type(self)))

class MutableSet(Mutable, Set, collections.MutableSet):

    @abc.abstractmethod
    def add(self, itm):
        """Add Item to Set"""
        pass

    @abc.abstractmethod
    def discard(self, itm):
        """Remove Item from Set if Present"""
        pass

class Mapping(Container, Iterable, Sized, collections.Mapping):

    def __getitem__(self, key):
        """Get Mapping Item"""
        return self.get_val()[key]

class MutableMapping(Mutable, Mapping, collections.MutableMapping):

    @abc.abstractmethod
    def __setitem__(self, key, val):
        """Set Mapping Item"""
        pass

    @abc.abstractmethod
    def __delitem__(self, key):
        """Delete Mapping Item"""
        pass
