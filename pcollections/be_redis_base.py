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

    def _to_bytes(self, str_in):

        if isinstance(str_in, bytes):
            str_out = str_in
        elif isinstance(str_in, str) or isinstance(str_in, native_str) :
            str_out = bytes(str_in.encode(constants.ENCODING))
        else:
            raise TypeError("{} not supported in string".format(type(str_in)))

        return str_out

    def _to_str(self, str_in):

        if isinstance(str_in, bytes):
            str_out = str(str_in.decode(constants.ENCODING))
        elif isinstance(str_in, str) or isinstance(str_in, native_str) :
            str_out = str_in
        else:
            raise TypeError("{} not supported in string".format(type(str_in)))

        return str_out

    def _get_bytes(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.get(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Bytes Object
        return self._to_bytes(ret[0])

    def _get_val(self):

        # Return Strings Object
        return self._to_str(self._get_bytes())

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = self._to_bytes(val)

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

    def _to_bytes(self, lst_in):

        lst_out = list()

        for item in lst_in:
            if (isinstance(item, bytes)):
                pass
            elif (isinstance(item, str) or isinstance(item, native_str)):
                item = bytes(item.encode(constants.ENCODING))
            else:
                raise TypeError("{} not supported in list".format(type(item)))
            lst_out.append(item)

        return lst_out

    def _to_str(self, lst_in):

        lst_out = list()

        for item in lst_in:
            if (isinstance(item, bytes)):
                item = str(item.decode(constants.ENCODING))
            elif (isinstance(item, str) or isinstance(item, native_str)):
                pass
            else:
                raise TypeError("{} not supported in list".format(type(v)))
            lst_out.append(item)

        return lst_out

    def _get_bytes(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.lrange(self._redis_key, 0, -1)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Bytes Object
        return self._to_bytes(ret[0])

    def _get_val(self):

        # Return Strings Object
        return self._to_str(self._get_bytes())

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = self._to_bytes(val)

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

    def _to_bytes(self, set_in):

        set_out = set()

        for item in set_in:
            if (isinstance(item, bytes)):
                pass
            elif (isinstance(item, str) or isinstance(item, native_str)):
                item = bytes(item.encode(constants.ENCODING))
            else:
                raise TypeError("{} not supported in set".format(type(item)))
            set_out.add(item)

        return set_out

    def _to_str(self, set_in):

        set_out = set()

        for item in set_in:
            if (isinstance(item, bytes)):
                item = str(item.decode(constants.ENCODING))
            elif (isinstance(item, str) or isinstance(item, native_str)):
                pass
            else:
                raise TypeError("{} not supported in set".format(type(v)))
            set_out.add(item)

        return set_out

    def _get_bytes(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.smembers(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Bytes Object
        return self._to_bytes(ret[0])

    def _get_val(self):

        # Return Strings Object
        return self._to_str(self._get_bytes())

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = self._to_bytes(val)

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

    def _to_bytes(self, dict_in):

        dict_in = dict(dict_in)
        dict_out = dict()

        for key, val in viewitems(dict_in):
            if (isinstance(key, bytes)):
                pass
            elif (isinstance(key, str) or isinstance(key, native_str)):
                key = bytes(key.encode(constants.ENCODING))
            else:
                raise TypeError("{} not supported in dictionary".format(type(val)))
            if (isinstance(val, bytes)):
                pass
            elif (isinstance(val, str) or isinstance(val, native_str)):
                val = bytes(val.encode(constants.ENCODING))
            else:
                raise TypeError("{} not supported in dictionary".format(type(val)))
            dict_out[key] = val

        return dict_out

    def _to_str(self, dict_in):

        dict_in = dict(dict_in)
        dict_out = dict()

        for key, val in viewitems(dict_in):
            if (isinstance(key, bytes)):
                key = str(key.decode(constants.ENCODING))
            elif (isinstance(key, str) or isinstance(key, native_str)):
                pass
            else:
                raise TypeError("{} not supported in dictionary".format(type(val)))
            if (isinstance(val, bytes)):
                val = str(val.decode(constants.ENCODING))
            elif (isinstance(val, str) or isinstance(val, native_str)):
                pass
            else:
                raise TypeError("{} not supported in dictionary".format(type(val)))
            dict_out[key] = val

        return dict_out

    def _get_bytes(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise exceptions.ObjectDNE(self)
            pipe.multi()
            pipe.hgetall(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Bytes Object
        return self._to_bytes(ret[0])

    def _get_val(self):

        # Return Strings Object
        return self._to_str(self._get_bytes())

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = self._to_bytes(val)

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
