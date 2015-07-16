# -*- coding: utf-8 -*-

# Andy Sayler
# 2014, 2015
# University of Colorado


### Imports ###

import redis

import base_redis
import atomic_abc

### Driver ###

class Driver(base_redis.Driver):
    pass


### Base Objects ###

class Sequence(base_redis.Sequence, atomic_abc.Sequence):
    pass

class MutableSequence(Sequence,
                      base_redis.MutableSequence, atomic_abc.MutableSequence):
    pass


### Objects ###

class String(Sequence,
             base_redis.String, atomic_abc.String):
    pass

class MutableString(MutableSequence, String,
                    base_redis.MutableString, atomic_abc.String):
    pass

class List(Sequence,
           base_redis.List, atomic_abc.List):
    pass

class MutableList(MutableSequence, List,
                  base_redis.MutableList, atomic_abc.MutableList):
    pass
