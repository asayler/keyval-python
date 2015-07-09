# -*- coding: utf-8 -*-

# Andy Sayler
# 2014, 2015
# University of Colorado


### Imports ###

import redis

import base
import base_abc


### Constants ###

_SEP_FIELD = ':'
_PREFIX_STRING = "string"
_PREFIX_LIST = "list"
_PREFIX_SET = "set"
_PREFIX_MAPPING = "hash"
_INDEX_KEY = "_obj_index"


### Driver ###

class Driver(redis.StrictRedis):

    pass


### Base Objects ###

class Persistent(base_abc.Persistent):

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
                    raise base.ObjectDNE(self)
            pipe.multi()
            pipe.delete(self._redis_key)
            self._unregister(pipe)

        # Delete Object
        self._driver.transaction(atomic_rem, self._redis_key)

class Mutable(Persistent, base_abc.Mutable):
    pass

class Container(Persistent, base_abc.Container):
    pass

class Iterable(Persistent, base_abc.Iterable):
    pass

class Sized(Persistent, base_abc.Sized):
    pass

class Sequence(Container, Iterable, Sized, base_abc.Sequence):
    pass

class MutableSequence(Mutable, Sequence, base_abc.MutableSequence):
    pass

class BaseSet(Container, Iterable, Sized, base_abc.BaseSet):
    pass

class MutableBaseSet(Mutable, BaseSet, base_abc.MutableBaseSet):
    pass

class Mapping(Container, Iterable, Sized, base_abc.Mapping):
    pass

class MutableMapping(Mutable, Mapping, base_abc.MutableMapping):
    pass

### Objects ###

class String(Sequence, base_abc.String):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(String, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_STRING, _SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.get(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return str(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        if val is None:
            raise TypeError("val must not be None")
        val = str(val)

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise base.ObjectExists(self)
            if not create and not exists:
                raise base.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.set(self._redis_key, val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableString(String, base_abc.MutableString):

    def __setitem__(self, idx, itm):
        """Set Seq Item"""

        # Check Input
        itm = str(itm)
        if len(itm) != 1:
            raise ValueError("{:s} must be a single charecter".format(v))

        # Transaction
        def atomic_setitem(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Check Index
            length = pipe.strlen(self._redis_key)
            if (idx >= length) or (idx < -length):
                raise IndexError("{:d} out of range".format(idx))

            # Normalize Index
            if (idx >= 0):
                idx_norm = idx
            else:
                idx_norm = length + idx

            # Set Item
            pipe.multi()
            pipe.setrange(self._redis_key, idx_norm, itm)

        # Execute Transaction
        self._driver.transaction(atomic_setitem, self._redis_key)

    def __delitem__(self, del_idx):
        """Del Seq Item"""

        # Transaction
        def atomic_del(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Check Index
            length = pipe.strlen(self._redis_key)
            if del_idx is None:
                idx = (length-1)
            else:
                idx = del_idx
            if (idx >= length) or (idx < -length):
                raise IndexError("{:d} out of range".format(idx))

            # Get Ranges
            if (idx == 0) or (idx == -length):
                start = ""
            else:
                start = pipe.getrange(self._redis_key, 0, (idx-1))
            if (idx == (length-1)) or (idx == -1):
                end = ""
            else:
                end = pipe.getrange(self._redis_key, (idx+1), length)

            # Set New Val
            new = start + end
            pipe.multi()
            pipe.set(self._redis_key, new)

        # Execute Transaction
        ret = self._driver.transaction(atomic_del, self._redis_key)

    def insert(self, idx, itm):
        """Insert Seq Item"""

        # Validate Input
        itm = str(itm)
        if len(itm) != 1:
            raise ValueError("{:s} must be a single charecter".format(itm))

        # Transaction
        def atomic_insert(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Get Ranges
            length = pipe.strlen(self._redis_key)
            if (idx == 0) or (idx <= -length):
                start = ""
            else:
                start = pipe.getrange(self._redis_key, 0, (idx-1))
            if (idx >= length):
                end = ""
            else:
                end = pipe.getrange(self._redis_key, idx, length)

            # Set New Val
            new = start + itm + end
            pipe.multi()
            pipe.set(self._redis_key, new)

        # Execute Transaction
        self._driver.transaction(atomic_insert, self._redis_key)

class List(Sequence, base_abc.List):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(List, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_LIST, _SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.lrange(self._redis_key, 0, -1)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return list(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = list(val)
        types = set([type(v) for v in val])
        for typ in types:
            if (typ is str):
                pass
            else:
                raise TypeError("{} not supported in seq".format(typ))

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise base.ObjectExists(self)
            if not create and not exists:
                raise base.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.rpush(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableList(List, base_abc.MutableList):

    def __setitem__(self, idx, itm):
        """Set Seq Item"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in seq".format(type(itm)))

        # Transaction
        def atomic_setitem(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Check Index
            length = pipe.llen(self._redis_key)
            if (idx >= length) or (idx < -length):
                raise IndexError("{:d} out of range".format(idx))

            # Normalize Index
            if (idx >= 0):
                idx_norm = idx
            else:
                idx_norm = length + idx

            # Set Item
            pipe.multi()
            pipe.lset(self._redis_key, idx_norm, itm)

        # Execute Transaction
        self._driver.transaction(atomic_setitem, self._redis_key)

    def __delitem__(self, del_idx):
        """Del Seq Item"""

        def atomic_del(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Check Index
            length = pipe.llen(self._redis_key)
            if del_idx is None:
                idx = (length-1)
            else:
                idx = del_idx
            if (idx >= length) or (idx < -length):
                raise IndexError("{:d} out of range".format(idx))

            # Get Ranges
            if (idx == 0) or (idx == -length):
                start = []
            else:
                start = pipe.lrange(self._redis_key, 0, (idx-1))
            if (idx == (length-1)) or (idx == -1):
                end = []
            else:
                end = pipe.lrange(self._redis_key, (idx+1), length)

            # Set New Val
            new = start + end
            pipe.multi()
            pipe.delete(self._redis_key)
            pipe.rpush(self._redis_key, *new)

        # Execute Transaction
        ret = self._driver.transaction(atomic_del, self._redis_key)

    def insert(self, idx, itm):
        """Insert Seq Item"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in seq".format(type(itm)))

        # Transaction
        def atomic_insert(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Get Ranges
            length = pipe.llen(self._redis_key)
            if (idx == 0) or (idx <= -length):
                start = []
            else:
                start = pipe.lrange(self._redis_key, 0, (idx-1))
            if (idx >= length):
                end = []
            else:
                end = pipe.lrange(self._redis_key, idx, length)

            # Set New Val
            new = start + [itm] + end
            pipe.multi()
            pipe.delete(self._redis_key)
            pipe.rpush(self._redis_key, *new)

        # Execute Transaction
        self._driver.transaction(atomic_insert, self._redis_key)

class Set(BaseSet, base_abc.Set):

    def __init__(self, driver, key):
        """Set Constructor"""

        # Call Parent
        super(Set, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_SET, _SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.smembers(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return set(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = set(val)
        types = set([type(v) for v in val])
        for typ in types:
            if (typ is str):
                pass
            else:
                raise TypeError("{} not supported in set".format(typ))

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise base.ObjectExists(self)
            if not create and not exists:
                raise base.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableSet(MutableBaseSet, Set, base_abc.MutableSet):

    def add(self, itm):
        """Add Item to Set"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in set".format(type(itm)))

        # Set Transaction
        def atomic_add(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Add Item
            pipe.multi()
            pipe.sadd(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(atomic_add, self._redis_key)

    def discard(self, itm):
        """Remove Item from Set if Present"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in set".format(type(itm)))

        # Set Transaction
        def atomic_discard(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.srem(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(atomic_discard, self._redis_key)

class Dictionary(Mapping, base_abc.Dictionary):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(Dictionary, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_MAPPING, _SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def atomic_get(pipe):

            if not self._exists(pipe):
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.hgetall(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_get, self._redis_key)

        # Return Object
        return dict(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        val = dict(val)
        types = set([type(v) for v in val.values()])
        for typ in types:
            if (typ is str):
                pass
            else:
                raise TypeError("{} not supported in mapping".format(typ))

        # Set Transaction
        def atomic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise base.ObjectExists(self)
            if not create and not exists:
                raise base.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.hmset(self._redis_key, val)

        # Execute Transaction
        self._driver.transaction(atomic_set, self._redis_key)

class MutableDictionary(MutableMapping, Dictionary, base_abc.MutableDictionary):

    def __setitem__(self, key, val):
        """Set Mapping Item"""

        # Validate Input
        if (type(key) is not str):
            raise TypeError("{} not supported as mapping key".format(type(key)))
        if (type(val) is not str):
            raise TypeError("{} not supported as mapping val".format(type(val)))

        # Transaction
        def atomic_setitem(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Set Item
            pipe.multi()
            pipe.hset(self._redis_key, key, val)

        # Execute Transaction
        self._driver.transaction(atomic_setitem, self._redis_key)

    def __delitem__(self, key):
        """Delete Mapping Item"""

        # Validate Input
        if (type(key) is not str):
            raise TypeError("{} not supported as mapping key".format(type(key)))

        # Transaction
        def atomic_delitem(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Check Key
            key_exists = pipe.hexists(self._redis_key, key)
            if not key_exists:
                raise KeyError("KeyError: '{}'".format(key))

            # Set Item
            pipe.multi()
            pipe.hdel(self._redis_key, key)

        # Execute Transaction
        self._driver.transaction(atomic_delitem, self._redis_key)
