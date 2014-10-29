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

    def _get_val(self):

        # Get Transaction
        def automic_get(pipe):

            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.get(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(automic_get, self._redis_key)

        # Return Object
        return ret[0]

    def _set_val(self, val, create=True, overwrite=True):

        # Set Transaction
        def automic_set(pipe):

            exists = pipe.exists(self._redis_key)
            if not overwrite and exists:
                raise base.ObjectExists(self)
            if not create and not exists:
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.set(self._redis_key, str(val))

        # Execute Transaction
        ret = self._driver.transaction(automic_set, self._redis_key)

        # Return Object
        return ret[0]

class MutableString(base_abc.MutableString, String):

    def __setitem__(self, i, v):
        """Set Seq Item"""

        # Check Input
        v = str(v)
        if len(v) != 1:
            raise ValueError("{:s} must be a single charecter".format(v))

        self._driver.setrange(self._redis_key, i, v)

    def __delitem__(self, i):
        """Del Seq Item"""

        val = self.get_val()
        new = ""

        for cnt in range(len(val)):
            if cnt != i:
                new += val[cnt]

        self.set_val(new)

    def insert(self, i, v):
        """Insert Seq Item"""

        # Check Input
        v = str(v)
        if len(v) != 1:
            raise ValueError("{:s} must be a single charecter".format(v))

        # Set Transaction
        def automic_insert(pipe):

            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)
            if (i > 0):
                start = pipe.getrange(self._redis_key, 0, i-1)
            else:
                start = ""
            end = pipe.getrange(self._redis_key, i, -1)
            new = start + v + end
            pipe.multi()
            pipe.set(self._redis_key, new)

        # Execute Transaction
        ret = self._driver.transaction(automic_insert, self._redis_key)

        # Return Object
        return ret[0]
