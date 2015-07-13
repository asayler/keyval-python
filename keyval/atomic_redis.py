# -*- coding: utf-8 -*-

# Andy Sayler
# 2014, 2015
# University of Colorado


### Imports ###

import redis

import base_redis
import atomic_abc

class Sequence(base_redis.Sequence, atomic_abc.Sequence):
    pass

class MutableSequence(base_redis.MutableSequence, atomic_abc.MutableSequence):
    pass
