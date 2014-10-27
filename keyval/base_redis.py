# -*- coding: utf-8 -*-

# Andy Sayler
# Fall 2014
# Univerity of Colorado


import redis

import base
import base_abc


_PREFIX_STRING = "string"


### Driver ###

class Driver(redis.StrictRedis):

    pass


### Base Objects ###

class Persistent(base_abc.Persistent):

    def rem(self):
        """Delete Object"""

        # Delete Object
        self._driver.delete(self._redis_key)

        # Call Parent
        super(Persistent, self).rem()

    def exists(self):
        """Check if Object Exists"""

        # Check Existence
        return self._driver.exists(self._redis_key)

class Sequence(base_abc.Sequence, Persistent):

    pass


### Objects ###

class String(base_abc.String, Sequence):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(String, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_STRING, base._SEP_FIELD, self._key)
        self._redis_key = redis_key

    @classmethod
    def from_new(cls, driver, key, val, *args, **kwargs):
        """New Constructor"""

        # Call Parent
        obj = super(String, cls).from_new(driver, key, *args, **kwargs)

        # Create Object
        ret = obj._driver.setnx(obj._redis_key, val)
        if not ret:
            raise base.ObjectExists(obj)

        # Return Object
        return obj

    def get_val(self):
        """Get Value as Corresponding Python Object"""

        # Get Object
        return self._driver.get(self._redis_key)

    def __len__(self):
        """Get Length of String"""

        # Get Length
        return self._driver.strlen(self._redis_key)
