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

    def __delitem__(self, idx):
        """Del Seq Item"""
        self.pop(idx)

### Abstract Objects ###

class String(Sequence, base_abc.String):
    pass

class MutableString(MutableSequence, String):
    pass

class List(Sequence, base_abc.List):
    pass

class MutableList(MutableSequence, List):
    pass
