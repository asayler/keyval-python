# -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015
# pcollections Package


### Imports ###

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from future.utils import native_str
from builtins import *

import abc

import redis

from . import exceptions
from . import constants
from . import abc_base


### Constants ###

_SEP_FIELD = ':'
_PREFIX_STRING = "string"
_PREFIX_LIST = "list"
_PREFIX_SET = "set"
_PREFIX_DICTIONARY = "hash"
_INDEX_KEY = "_obj_index"


### Driver ###

class Driver(redis.StrictRedis):

    pass


### Base Objects ###

class Persistent(abc_base.Persistent):

    def _register(self, pipe):
        """Register Object as Existing"""

        pipe.sadd(_INDEX_KEY, self._redis_key)

    def _unregister(self, pipe):
        """Unregister Object as Existing"""

        pipe.srem(_INDEX_KEY, self._redis_key)

    def _exists(self, pipe):
        """Check if Object Exists (Immediate)"""

        return bool(pipe.sismember(_INDEX_KEY, self._redis_key))

    def exists(self):
        """Check if Object Exists (Transaction)"""

        # Exists Transaction
        def atomic_exists(pipe):

            pipe.multi()
            pipe.sismember(_INDEX_KEY, self._redis_key)

        # Check if Object Exists
        ret = self._driver.transaction(atomic_exists, self._redis_key)

        # Return Bool
        return bool(ret[0])

    def rem(self, force=False):
        """Delete Object"""

        # Delete Transaction
        def atomic_rem(pipe):

            if not self._exists(pipe):
                if force:
                    return
                else:
                    raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.delete(self._redis_key)
            self._unregister(pipe)

        # Delete Object
        self._driver.transaction(atomic_rem, self._redis_key)

    @abc.abstractmethod
    def __init__(self, driver, key, prefix):
        """ Constructor"""

        # Call Parent
        super(Persistent, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(prefix, _SEP_FIELD, self._key)
        self._redis_key = redis_key


### Objects ###

class String(Persistent, abc_base.String):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(String, self).__init__(driver, key, _PREFIX_STRING)

    def _get_bytes(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.get(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Convert to Bytes
        data = ret[0]
        if (isinstance(data, str) or isinstance(data, native_str)):
            data = data.encode(constants.ENCODING)
        assert isinstance(data, bytes)

        # Return Bytes
        return data

    def _get_val(self):

        data = str(self._get_bytes().decode(constants.ENCODING))
        assert isinstance(data, str)
        return data

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        if not (isinstance(val, str) or isinstance(val, native_str)):
            raise TypeError("{} not supported in string".format(type(val)))
        val = val.encode(constants.ENCODING)

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise exceptions.ObjectExists(self)
            if not create and not exists:
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.set(self._redis_key, val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableString(String, abc_base.MutableString):
    pass

class List(Persistent, abc_base.List):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(List, self).__init__(driver, key, _PREFIX_LIST)

    def _get_bytes(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.lrange(self._redis_key, 0, -1)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Convert to Bytes
        lst_in = ret[0]
        lst_out = []
        for item in lst_in:
            if (isinstance(item, str) or isinstance(item, native_str)):
                item = item.encode(constants.ENCODING)
            assert isinstance(item, bytes)
            lst_out.append(item)

        # Return Object
        return lst_out

    def _get_val(self):

        lst_bytes = self._get_bytes()
        lst_str = []
        for item in lst_bytes:
            item = str(item.decode(constants.ENCODING))
            assert isinstance(item, str)
            lst_str.append(item)
        return lst_str

    def _set_val(self, val_in, create=True, overwrite=True):

        # Validate Input
        val_in = list(val_in)
        val_out = []
        for item in val_in:
            if not (isinstance(item, str) or isinstance(item, native_str)):
                raise TypeError("{} not supported in seq".format(type(item)))
            item = item.encode(constants.ENCODING)
            val_out.append(item)

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise exceptions.ObjectExists(self)
            if not create and not exists:
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val_out) > 0:
                pipe.rpush(self._redis_key, *val_out)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableList(List, abc_base.MutableList):
    pass

class Set(Persistent, abc_base.Set):

    def __init__(self, driver, key):
        """Set Constructor"""

        # Call Parent
        super(Set, self).__init__(driver, key, _PREFIX_SET)

    def _get_bytes(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.smembers(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Convert to Bytes
        set_in = ret[0]
        set_out = set()
        for item in set_in:
            if (isinstance(item, bytes)):
                pass
            elif (isinstance(item, str) or isinstance(item, native_str)):
                item = bytes(item.encode(constants.ENCODING))
            else:
                raise TypeError("{} not supported in set".format(type(v)))
            set_out.add(item)

        # Return Object
        return set_out

    def _get_val(self):

        set_bytes = self._get_bytes()
        set_str = set()
        for item in set_bytes:
            item = str(item.decode(constants.ENCODING))
            set_str.add(item)
        return set_str

    def _set_val(self, val_in, create=True, overwrite=True):

        # Validate Input
        val_in = set(val_in)
        val_out = set()
        for item in val_in:
            if (isinstance(item, bytes)):
                pass
            elif (isinstance(item, str) or isinstance(item, native_str)):
                item = bytes(item.encode(constants.ENCODING)                )
            else:
                raise TypeError("{} not supported in set".format(type(item)))
            val_out.add(item)

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise exceptions.ObjectExists(self)
            if not create and not exists:
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val_out) > 0:
                pipe.sadd(self._redis_key, *val_out)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableSet(Set, abc_base.MutableSet):
    pass

class Dictionary(Persistent, abc_base.Dictionary):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(Dictionary, self).__init__(driver, key, _PREFIX_DICTIONARY)

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.hgetall(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return dict(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = dict(val)
        for v in val.values():
            if not (isinstance(v, str) or isinstance(v, native_str)):
                raise TypeError("{} not supported in set".format(type(v)))

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise exceptions.ObjectExists(self)
            if not create and not exists:
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.hmset(self._redis_key, val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableDictionary(Dictionary, abc_base.MutableDictionary):
    pass
