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

    def rem(self, force=False):
        """Delete Object"""

        # Delete Transaction
        def automic_rem(pipe):

            exists = pipe.exists(self._redis_key)
            if not exists:
                if force:
                    return
                else:
                    raise base.ObjectDNE(self)
            pipe.multi()
            pipe.delete(self._redis_key)

        # Delete Object
        self._driver.transaction(automic_rem, self._redis_key)

        # Call Parent
        super(Persistent, self).rem(force=force)

    def exists(self):
        """Check if Object Exists"""

        # Check Existence
        return self._driver.exists(self._redis_key)

class Mutable(base_abc.Mutable, Persistent):

    pass

class Sequence(base_abc.Sequence, Persistent):

    pass

class MutableSequence(base_abc.MutableSequence, Sequence, Mutable):

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
        ret = obj._driver.setnx(obj._redis_key, str(val))
        if not ret:
            raise base.ObjectExists(obj)

        # Return Object
        return obj

    def get_val(self):
        """Get Value as Corresponding Python Object"""

        # Get Transaction
        def automic_rem(pipe):

            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.get(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(automic_rem, self._redis_key)

        # Return Object
        return ret[0]

    def __len__(self):
        """Get Length of String"""

        # Get Length
        return self._driver.strlen(self._redis_key)

class MutableString(base_abc.MutableString, String):

    def set_val(self, val):
        """Set Value of Persistent Object"""

        self._driver.set(self._redis_key, str(val))

    def __setitem__(self, i, val):
        """Set Seq Item"""

        self._driver.set(self._redis_key, i, str(val))

    def __delitem__(self, i):
        """Del Seq Item"""
        raise NotImplementedError("__delitem__ not yet implemented")

    def insert(self, i, x):
        """Insert Seq Item"""
        raise NotImplementedError("__insert__ not yet implemented")
