# -*- coding: utf-8 -*-

# Andy Sayler
# Fall 2014
# Univerity of Colorado


import redis

import base
import base_abc


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
        def automic_exists(pipe):

            pipe.multi()
            pipe.sismember(_INDEX_KEY, self._redis_key)

        # Check if Object Exists
        ret = self._driver.transaction(automic_exists, self._redis_key)

        # Return Bool
        return bool(ret[0])

    def rem(self, force=False):
        """Delete Object"""

        # Delete Transaction
        def automic_rem(pipe):

            if not self._exists(pipe):
                if force:
                    return
                else:
                    raise base.ObjectDNE(self)
            pipe.multi()
            pipe.delete(self._redis_key)
            self._unregister(pipe)

        # Delete Object
        self._driver.transaction(automic_rem, self._redis_key)

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


### Objects ###

class String(Sequence, base_abc.String):

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

            if not self._exists(pipe):
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.get(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(automic_get, self._redis_key)

        # Return Object
        return str(ret[0])

    def _set_val(self, val, create=True, overwrite=True):

        # Validate Input
        if val is None:
            raise TypeError("val must not be None")
        val = str(val)

        # Set Transaction
        def automic_set(pipe):

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
        self._driver.transaction(automic_set, self._redis_key)

class MutableString(String, base_abc.MutableString):

    def __setitem__(self, idx, itm):
        """Set Seq Item"""

        # Check Input
        itm = str(itm)
        if len(itm) != 1:
            raise ValueError("{:s} must be a single charecter".format(v))

        # Transaction
        def automic_setitem(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
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
        self._driver.transaction(automic_setitem, self._redis_key)

    def insert(self, idx, itm):
        """Insert Seq Item"""

        # Validate Input
        itm = str(itm)
        if len(itm) != 1:
            raise ValueError("{:s} must be a single charecter".format(itm))

        # Transaction
        def automic_insert(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
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
        self._driver.transaction(automic_insert, self._redis_key)

    def append(self, itm):
        """Append Seq Item"""

        # Validate Input
        v = str(itm)
        if len(itm) != 1:
            raise ValueError("{:s} must be a single charecter".format(itm))

        # Transaction
        def automic_append(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Append
            pipe.multi()
            pipe.append(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(automic_append, self._redis_key)

    def extend(self, seq):
        """Append Seq wuth another Seq"""

        # Validate Input
        seq = str(seq)

        # Transaction
        def automic_extend(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Extend
            pipe.multi()
            pipe.append(self._redis_key, seq)

        # Execute Transaction
        if len(seq):
            self._driver.transaction(automic_extend, self._redis_key)
        else:
            pass

    def reverse(self):
        """Reverse Seq"""

        # Transaction
        def automic_reverse(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Read
            seq = pipe.get(self._redis_key)

            # Reverse
            rev = seq[::-1]

            # Write
            pipe.multi()
            pipe.set(self._redis_key, rev)

        # Execute Transaction
        self._driver.transaction(automic_reverse, self._redis_key)

    def pop(self, pop_idx=None):
        """Pop Seq Item"""

        # Transaction
        def automic_pop(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Check Index
            length = pipe.strlen(self._redis_key)
            if pop_idx is None:
                idx = (length-1)
            else:
                idx = pop_idx
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
            pipe.getrange(self._redis_key, idx, idx)
            pipe.set(self._redis_key, new)

        # Execute Transaction
        ret = self._driver.transaction(automic_pop, self._redis_key)
        return str(ret[0])

    def remove(self, itm):
        """Remove itm from Seq"""

        # Validate Input
        itm = str(itm)
        if len(itm) != 1:
            raise ValueError("{:s} must be a single charecter".format(itm))

        # Transaction
        def automic_remove(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Get idx
            seq = pipe.get(self._redis_key)
            idx = seq.index(itm)

            # Get Ranges
            length = pipe.strlen(self._redis_key)
            if (idx == 0):
                start = ""
            else:
                start = pipe.getrange(self._redis_key, 0, (idx-1))
            if (idx == (length-1)):
                end = ""
            else:
                end = pipe.getrange(self._redis_key, (idx+1), length)

            # Set New Val
            new = start + end

            # Write
            pipe.multi()
            pipe.set(self._redis_key, new)

        # Execute Transaction
        self._driver.transaction(automic_remove, self._redis_key)

class List(Sequence, base_abc.List):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(List, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_LIST, base._SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def automic_get(pipe):

            if not self._exists(pipe):
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.lrange(self._redis_key, 0, -1)

        # Execute Transaction
        ret = self._driver.transaction(automic_get, self._redis_key)

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
        def automic_set(pipe):

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
        self._driver.transaction(automic_set, self._redis_key)

class MutableList(List, base_abc.MutableList):

    def __setitem__(self, idx, itm):
        """Set Seq Item"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in seq".format(type(itm)))

        # Transaction
        def automic_setitem(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
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
        self._driver.transaction(automic_setitem, self._redis_key)

    def insert(self, idx, itm):
        """Insert Seq Item"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in seq".format(type(itm)))

        # Transaction
        def automic_insert(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
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
        self._driver.transaction(automic_insert, self._redis_key)

    def append(self, itm):
        """Append Seq Item"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in seq".format(type(itm)))

        # Transaction
        def automic_append(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Append
            pipe.multi()
            pipe.rpush(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(automic_append, self._redis_key)

    def extend(self, seq):
        """Append Seq wuth another Seq"""

        # Validate Input
        seq = list(seq)
        types = set([type(v) for v in seq])
        for typ in types:
            if (typ is str):
                pass
            else:
                raise TypeError("{} not supported in seq".format(typ))

        # Transaction
        def automic_extend(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Extend
            pipe.multi()
            pipe.rpush(self._redis_key, *seq)

        # Execute Transaction
        if len(seq):
            self._driver.transaction(automic_extend, self._redis_key)
        else:
            pass

    def reverse(self):
        """Reverse Seq"""

        # Transaction
        def automic_reverse(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Read
            seq = pipe.lrange(self._redis_key, 0, -1)

            # Reverse
            rev = seq[::-1]

            # Write
            pipe.multi()
            pipe.delete(self._redis_key)
            pipe.rpush(self._redis_key, *rev)

        # Execute Transaction
        self._driver.transaction(automic_reverse, self._redis_key)

    def pop(self, pop_idx=None):
        """Pop Seq Item"""

        # Transaction
        def automic_pop(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Check Index
            length = pipe.llen(self._redis_key)
            if pop_idx is None:
                idx = (length-1)
            else:
                idx = pop_idx
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
            pipe.lrange(self._redis_key, idx, idx)
            pipe.delete(self._redis_key)
            pipe.rpush(self._redis_key, *new)

        # Execute Transaction
        ret = self._driver.transaction(automic_pop, self._redis_key)
        return str(ret[0][0])

    def remove(self, itm):
        """Remove itm from Seq"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in seq".format(type(itm)))

        # Transaction
        def automic_remove(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Write
            pipe.multi()
            pipe.lrem(self._redis_key, 1, itm)

        # Execute Transaction
        ret = self._driver.transaction(automic_remove, self._redis_key)

        # Check result
        if (ret[0] != 1):
            raise ValueError("'{}' is not in list".format(itm))

class Set(Container, Iterable, Sized, base_abc.Set):

    def __init__(self, driver, key):
        """Set Constructor"""

        # Call Parent
        super(Set, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_SET, base._SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def automic_get(pipe):

            if not self._exists(pipe):
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.smembers(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(automic_get, self._redis_key)

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
        def automic_set(pipe):

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
        self._driver.transaction(automic_set, self._redis_key)

class MutableSet(Mutable, Set, base_abc.MutableSet):

    def add(self, itm):
        """Add Item to Set"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in set".format(type(itm)))

        # Set Transaction
        def automic_add(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Add Item
            pipe.multi()
            pipe.sadd(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(automic_add, self._redis_key)

    def discard(self, itm):
        """Remove Item from Set if Present"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in set".format(type(itm)))

        # Set Transaction
        def automic_discard(pipe):

            # Check Exists
            exists = pipe.exists(self._redis_key)
            if not exists:
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.srem(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(automic_discard, self._redis_key)

class Mapping(Container, Iterable, Sized, base_abc.Mapping):

    def __init__(self, driver, key):
        """ Constructor"""

        # Call Parent
        super(Mapping, self).__init__(driver, key)

        # Save Extra Attrs
        redis_key = "{:s}{:s}{:s}".format(_PREFIX_MAPPING, base._SEP_FIELD, self._key)
        self._redis_key = redis_key

    def _get_val(self):

        # Get Transaction
        def automic_get(pipe):

            if not self._exists(pipe):
                raise base.ObjectDNE(self)
            pipe.multi()
            pipe.hgetall(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(automic_get, self._redis_key)

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
                raise TypeError("{} not supported in seq".format(typ))
        if len(val) == 0:
            raise ValueError("mapping must have non-zero length")

        # Set Transaction
        def automic_set(pipe):

            exists = self._exists(pipe)
            if not overwrite and exists:
                raise base.ObjectExists(self)
            if not create and not exists:
                raise base.ObjectDNE(self)
            pipe.multi()
            if create:
                self._register(pipe)
            pipe.delete(self._redis_key)
            pipe.hmset(self._redis_key, val)

        # Execute Transaction
        self._driver.transaction(automic_set, self._redis_key)
