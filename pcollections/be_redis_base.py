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
from future.utils import viewitems
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

    def _encode_val_item(self, item_in):
        """Encode single item as bytes"""

        item_out = None
        if isinstance(item_in, bytes):
            item_out = item_in
        elif isinstance(item_in, str) or isinstance(item_in, native_str):
            item_out = bytes(item_in.encode(constants.ENCODING))
        else:
            raise TypeError("Encoding type '{}' not supported".format(type(item_in)))
        return item_out

    def _decode_val_item(self, item_in):
        """Decode single item Python type"""

        item_out = None
        if isinstance(item_in, bytes):
            item_out = str(item_in.decode(constants.ENCODING))
        elif isinstance(item_in, str) or isinstance(item_in, native_str):
            item_out = item_in
        else:
            raise TypeError("Decoding '{}' not supported".format(type(item_in)))
        return item_out

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

    def _encode_val_object(self, obj_in):
        return self._encode_val_item(obj_in)

    def _decode_val_object(self, obj_in):
        return self._decode_val_item(obj_in)

    def _get_val_raw(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.get(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Raw
        return ret[0]

    def _set_val_raw(self, val, create=True, overwrite=True):

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

    def _encode_val_object(self, obj_in):

        obj_out = list()
        for item in obj_in:
            obj_out.append(self._encode_val_item(item))
        return obj_out

    def _decode_val_object(self, obj_in):

        obj_out = list()
        for item in obj_in:
            obj_out.append(self._decode_val_item(item))
        return obj_out

    def _get_val_raw(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.lrange(self._redis_key, 0, -1)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Raw
        return ret[0]

    def _set_val_raw(self, val, create=True, overwrite=True):

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
                pipe.rpush(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableList(List, abc_base.MutableList):
    pass

class Set(Persistent, abc_base.Set):

    def __init__(self, driver, key):
        """Set Constructor"""

        # Call Parent
        super(Set, self).__init__(driver, key, _PREFIX_SET)

    def _encode_val_object(self, obj_in):

        obj_out = set()
        for item in obj_in:
            obj_out.add(self._encode_val_item(item))
        return obj_out

    def _decode_val_object(self, obj_in):

        obj_out = set()
        for item in obj_in:
            obj_out.add(self._decode_val_item(item))
        return obj_out

    def _get_val_raw(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.smembers(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Raw
        return ret[0]

    def _set_val_raw(self, val, create=True, overwrite=True):

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
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableSet(Set, abc_base.MutableSet):
    pass

class Dictionary(Persistent, abc_base.Dictionary):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(Dictionary, self).__init__(driver, key, _PREFIX_DICTIONARY)

    def _encode_val_object(self, obj_in):

        obj_in = dict(obj_in)
        obj_out = dict()
        for key, val in viewitems(obj_in):
            key = self._encode_val_item(key)
            val = self._encode_val_item(val)
            obj_out[key] = val
        return obj_out

    def _decode_val_object(self, obj_in):

        obj_in = dict(obj_in)
        obj_out = dict()
        for key, val in viewitems(obj_in):
            key = self._decode_val_item(key)
            val = self._decode_val_item(val)
            obj_out[key] = val
        return obj_out

    def _get_val_raw(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.hgetall(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Raw
        return ret[0]

    def _set_val_raw(self, val, create=True, overwrite=True):

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
