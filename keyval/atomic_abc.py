# -*- coding: utf-8 -*-

# Andy Sayler
# 2014, 2015
# University of Colorado


### Imports ###
import abc

import base_abc


### Abstract Base Objects ###

class Sequence(base_abc.Sequence):
    pass

class MutableSequence(Sequence, base_abc.MutableSequence):

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

class BaseSet(base_abc.BaseSet):
    pass

class MutableBaseSet(BaseSet, base_abc.MutableBaseSet):

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

class Mapping(base_abc.Mapping):
    pass

class MutableMapping(Mapping, base_abc.MutableMapping):

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

    # @abc.abstractmethod
    # def setdefault(key, default=None):
    #     """Return Key or Set to Default"""
    #     raise NotImplementedError("setdefault not yet implemented")


### Abstract Objects ###

class String(Sequence, base_abc.String):
    pass

class MutableString(MutableSequence, String):
    pass

class List(Sequence, base_abc.List):
    pass

class MutableList(MutableSequence, List):
    pass

class Set(BaseSet, base_abc.Set):
    pass

class MutableSet(MutableBaseSet, Set):
    pass

class Dictionary(Mapping, base_abc.Dictionary):
    pass

class MutableDictionary(MutableMapping, Dictionary):
    pass
