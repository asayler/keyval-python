# -*- coding: utf-8 -*-

# Andy Sayler
# 2014, 2015
# University of Colorado


### Pylint ###
#pylint: disable=abstract-method


### Imports ###
import abc

import abc_base


### Abstract Base Objects ###

class Sequence(abc_base.Sequence):
    pass

class MutableSequence(Sequence, abc_base.MutableSequence):

    @abc.abstractmethod
    def append(self, itm):
        """Append Seq Item"""
        pass

    @abc.abstractmethod
    def reverse(self):
        """Reverse Seq"""
        pass

    @abc.abstractmethod
    def extend(self, seq):
        """Extend Seq with another Seq"""
        pass

    @abc.abstractmethod
    def pop(self, pop_idx=None):
        """Remove and return item"""
        pass

    @abc.abstractmethod
    def remove(self, itm):
        """Remove itm from seq"""
        pass

    def __iadd__(self, other):
        """+="""
        self.extend(other)
        return self

    def __delitem__(self, idx):
        """Del Seq Item"""
        self.pop(idx)

class BaseSet(abc_base.BaseSet):
    pass

class MutableBaseSet(BaseSet, abc_base.MutableBaseSet):

    @abc.abstractmethod
    def clear(self):
        """Clear Set"""
        pass

    @abc.abstractmethod
    def pop(self):
        """Pop item from Set"""
        pass

    @abc.abstractmethod
    def remove(self, itm):
        """Remote itm from set"""
        pass

    @abc.abstractmethod
    def __ior__(self, other):
        """Unary or"""
        pass

    @abc.abstractmethod
    def __iand__(self, other):
        """Unary and"""
        pass

    @abc.abstractmethod
    def __ixor__(self, other):
        """Unary xor"""
        pass

    @abc.abstractmethod
    def __isub__(self, other):
        """Unary subtract"""
        pass

class Mapping(abc_base.Mapping):
    pass

class MutableMapping(Mapping, abc_base.MutableMapping):

    @abc.abstractmethod
    def pop(self, *args):
        """Pop Specified Item"""
        pass

    @abc.abstractmethod
    def popitem(self):
        """Pop Arbitrary Item"""
        pass

    @abc.abstractmethod
    def clear(self):
        """Clear Dictionary"""
        pass

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        """Update Dictionary"""
        pass

    @abc.abstractmethod
    def setdefault(key, default=None):
        """
        Return Key or Set to Default

        setdefault(key[, default])

        If key is in the dictionary, return its value. If not, insert
        key with a value of default and return default. default
        defaults to None.
        """
        pass



### Abstract Objects ###

class String(Sequence, abc_base.String):
    pass

class MutableString(MutableSequence, String):
    pass

class List(Sequence, abc_base.List):
    pass

class MutableList(MutableSequence, List):
    pass

class Set(BaseSet, abc_base.Set):
    pass

class MutableSet(MutableBaseSet, Set):
    pass

class Dictionary(Mapping, abc_base.Dictionary):
    pass

class MutableDictionary(MutableMapping, Dictionary):
    pass
