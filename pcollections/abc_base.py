# -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015
# pcollections Package


### Pylint ###
#pylint: disable=abstract-method


### Imports ###

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from future.utils import native_str
from future.utils import with_metaclass
from future.utils import python_2_unicode_compatible
from builtins import *

import abc
import collections

from . import exceptions
from . import constants
from . import keys

### Abstract Base Objects ###

class Persistent(with_metaclass(abc.ABCMeta, object)):

    def __init__(self, driver, key, create=None, existing=None):
        """Object Constructor"""

        #                      existing  create
        # OPEN_EXISTING         True      None
        # OVERWRITE_EXISTING    True      Val
        # OPEN_ANY              None      None
        # CREATE_OR_OPEN        None      Val
        # CREATE_OR_FAIL        False     Val
        # OPEN_NONEXISTING      False     None

        # Check Input
        if driver is None:
            raise TypeError("driver must not be None")
        if key is None:
            raise TypeError("key must not be None")
        if not isinstance(key, keys.BaseKey):
            raise TypeError("key must by an instance of keys.BaseKey()")

        # Call Parent
        super(Persistent, self).__init__()

        # Save Attrs
        self._driver = driver
        self._key = key

        # Init Value
        self._init_val(create=create, existing=existing)

    @classmethod
    def from_new(cls, driver, key, val):
        """New Constructor"""
        if val is None:
            raise TypeError("val must not be None")
        return cls(driver, key, create=val, existing=False)

    @classmethod
    def from_existing(cls, driver, key):
        """Existing Constructor"""
        return cls(driver, key, create=None, existing=True)

    @classmethod
    def from_raw(cls, driver, key, create=None, existing=None):
        """Raw Constructor"""
        return cls(driver, key)

    @abc.abstractmethod
    def _encode_val_item(self, item_in, test=False):
        """Encode single item as backend type"""
        pass

    @abc.abstractmethod
    def _decode_val_item(self, item_in, test=False):
        """Decode single item as Python type"""
        pass

    @abc.abstractmethod
    def _map_conv_obj(self, obj_in, conv_func, test=False):
        """Map conv_func across nested object"""
        pass

    def _encode_val_obj(self, obj_in, test=False):
        """Encode nested object items as backend types"""
        return self._map_conv_obj(obj_in, self._encode_val_item, test=test)

    def _decode_val_obj(self, obj_in, test=False):
        """Decode nested object items as Python types"""
        return self._map_conv_obj(obj_in, self._decode_val_item, test=test)

    def _init_val(self, create=None, existing=None):
        """Init value from python types"""
        if create is not None:
            create = self._encode_val_obj(create)
        self._init_val_raw(create=create, existing=existing)

    @abc.abstractmethod
    def _init_val_raw(self, create=None, existing=None):
        """Init value from raw backend type"""
        pass

    def _set_val(self, val):
        """Set value as python types"""
        self._set_val_raw(self._encode_val_obj(val))

    @abc.abstractmethod
    def _set_val_raw(self, val):
        """Set value as raw backend type"""
        pass

    def get_val(self):
        """Get value as Python types"""
        return self._decode_val_obj(self._get_val_raw())

    @abc.abstractmethod
    def _get_val_raw(self):
        """Get value as raw backend type"""
        pass

    def get_key(self):
        """Get Key"""
        return self._key.key

    @abc.abstractmethod
    def exists(self):
        """Check if Object Exists"""
        pass

    def create(self, val):
        """Create Object"""
        if val is None:
            raise TypeError("val must not be None")
        self._init_val(create=val, existing=False)

    @abc.abstractmethod
    def rem(self, force=False):
        """Delete Object"""
        pass

    def __str__(self):
        """Return String Representation"""
        return str(self.get_val())

    def __repr__(self):
        """Return Unique Representation"""
        return self.get_key()

    def __bool__(self):
        """Test Bool"""
        return bool(self.get_val())

class Mutable(Persistent):

    def set_val(self, val):
        """Set Value of Persistent Object"""
        return self._set_val(val)

class Equality(Persistent):

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

class Comparable(Equality):

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

class MutableSequence(Sequence, Mutable, collections.MutableSequence):

    @abc.abstractmethod
    def __setitem__(self, idx, itm):
        """Set Seq Item"""
        pass

    @abc.abstractmethod
    def __delitem__(self, idx):
        """Del Seq Item"""
        pass

    @abc.abstractmethod
    def insert(self, idx, itm):
        """Insert Seq Item"""
        pass

class BaseSet(Comparable, Container, Iterable, Sized, collections.Set):

    def __and__(self, other):
        """Return Intersection"""
        if (type(other) == type(self)):
            return (self.get_val() & other.get_val())
        else:
            raise TypeError("Can only and {}".format(type(self)))

    def __or__(self, other):
        """Return Union"""
        if (type(other) == type(self)):
            return (self.get_val() | other.get_val())
        else:
            raise TypeError("Can only or {}".format(type(self)))

    def __xor__(self, other):
        """Return Symmetric Difference"""
        if (type(other) == type(self)):
            return (self.get_val() ^ other.get_val())
        else:
            raise TypeError("Can only xor {}".format(type(self)))

    def __sub__(self, other):
        """Return Difference"""
        if (type(other) == type(self)):
            return (self.get_val() - other.get_val())
        else:
            raise TypeError("Can only sub {}".format(type(self)))

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

    def intersection(self, other):
        """Return Intersection"""
        if (type(other) == type(self)):
            return (self.get_val().intersection(other.get_val()))
        else:
            raise TypeError("Can only intersect {}".format(type(self)))

    def union(self, other):
        """Return Union"""
        if (type(other) == type(self)):
            return (self.get_val().union(other.get_val()))
        else:
            raise TypeError("Can only union {}".format(type(self)))

    def difference(self, other):
        """Return Difference"""
        if (type(other) == type(self)):
            return (self.get_val().difference(other.get_val()))
        else:
            raise TypeError("Can only difference {}".format(type(self)))

    def symmetric_difference(self, other):
        """Return Symmetric Difference"""
        if (type(other) == type(self)):
            return (self.get_val().symmetric_difference(other.get_val()))
        else:
            raise TypeError("Can only symmetric_difference {}".format(type(self)))

class MutableBaseSet(BaseSet, Mutable, collections.MutableSet):

    @abc.abstractmethod
    def add(self, itm):
        """Add Item to Set"""
        pass

    @abc.abstractmethod
    def discard(self, itm):
        """Remove Item from Set if Present"""
        pass

class Mapping(Equality, Container, Iterable, Sized, collections.Mapping):

    def __getitem__(self, key):
        """Get Mapping Item"""
        return self.get_val()[key]

class MutableMapping(Mapping, Mutable, collections.MutableMapping):

    @abc.abstractmethod
    def __setitem__(self, key, val):
        """Set Mapping Item"""
        pass

    @abc.abstractmethod
    def __delitem__(self, key):
        """Delete Mapping Item"""
        pass

### Abstract Objects ###

class String(Sequence):
    pass

class MutableString(String, MutableSequence):

    def __setitem__(self, idx, item):
        """Set Seq Item"""

        # Get string
        val_in = self.get_val()
        length = len(val_in)

        # Check bounds
        if (idx >= length) or (idx < -length):
            raise IndexError("{:d} out of range".format(idx))

        # Generate new string
        val_out = ""
        if (idx != 0) and (idx != -len(val_in)):
            val_out += val_in[:idx]
        val_out += item
        if (idx != (len(val_in)-1)) and (idx != -1):
            val_out += val_in[idx+1:]

        # Set string
        self.set_val(val_out)

    def __delitem__(self, idx):
        """Del Seq Item"""

        # Get string
        val_in = self.get_val()
        length = len(val_in)

        # Check bounds
        if (idx >= length) or (idx < -length):
            raise IndexError("{:d} out of range".format(idx))

        # Generate new string
        val_out = ""
        if (idx != 0) and (idx != -len(val_in)):
            val_out += val_in[:idx]
        if (idx != (len(val_in)-1)) and (idx != -1):
            val_out += val_in[idx+1:]

        # Set string
        self.set_val(val_out)

    def insert(self, idx, item):
        """Insert Seq Item"""

        # Get String
        val_in = self.get_val()

        # No bounds check: slicing works without it

        # Generate new string
        val_out = val_in[:idx] + item + val_in[idx:]

        # Set string
        self.set_val(val_out)

class List(Sequence):
    pass

class MutableList(List, MutableSequence):

    def __setitem__(self, idx, itm):
        """Set Seq Item"""

        val = self.get_val()
        val[idx] = itm
        self.set_val(val)

    def __delitem__(self, idx):
        """Del Seq Item"""

        val = self.get_val()
        del(val[idx])
        self.set_val(val)

    def insert(self, idx, itm):
        """Insert Seq Item"""

        val = self.get_val()
        val.insert(idx, itm)
        self.set_val(val)

class Set(BaseSet):
    pass

class MutableSet(Set, MutableBaseSet):

    def add(self, itm):
        """Add Item to Set"""

        # Validate Input
        if not (isinstance(itm, str) or isinstance(itm, native_str)):
            raise TypeError("{} not supported in set".format(type(itm)))

        # R/U/W
        val = self.get_val()
        val.add(itm)
        self.set_val(val)

    def discard(self, itm):
        """Remove Item from Set if Present"""

        # Validate Input
        if not (isinstance(itm, str) or isinstance(itm, native_str)):
            raise TypeError("{} not supported in set".format(type(itm)))

        # R/U/W
        val = self.get_val()
        val.discard(itm)
        self.set_val(val)

class Dictionary(Mapping):
    pass

class MutableDictionary(Dictionary, MutableMapping):

    def __setitem__(self, key, itm):
        """Set Mapping Item"""

        val = self.get_val()
        val[key] = itm
        self.set_val(val)

    def __delitem__(self, key):
        """Delete Mapping Item"""

        val = self.get_val()
        del(val[key])
        self.set_val(val)
