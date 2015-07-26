# -*- coding: utf-8 -*-

# Andy Sayler
# 2014, 2015
# University of Colorado


### Imports ###

import redis

import base
import base_redis
import atomic_abc

### Driver ###

class Driver(base_redis.Driver):
    pass


### Base Objects ###

class Sequence(base_redis.Sequence, atomic_abc.Sequence):
    pass

class MutableSequence(Sequence, base_redis.MutableSequence, atomic_abc.MutableSequence):
    pass

class BaseSet(base_redis.BaseSet, atomic_abc.BaseSet):
    pass

class MutableBaseSet(BaseSet, base_redis.MutableBaseSet, atomic_abc.MutableBaseSet):
    pass

class Mapping(base_redis.Mapping, atomic_abc.Mapping):
    pass

class MutableMapping(Mapping, base_redis.MutableMapping, atomic_abc.MutableMapping):
    pass


### Objects ###

class String(Sequence, base_redis.String, atomic_abc.String):
    pass

class MutableString(MutableSequence, String, atomic_abc.MutableString):

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

    def append(self, itm):
        """Append Seq Item"""

        # Validate Input
        v = str(itm)
        if len(itm) != 1:
            raise ValueError("{:s} must be a single charecter".format(itm))

        # Transaction
        def atomic_append(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Append
            pipe.multi()
            pipe.append(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(atomic_append, self._redis_key)

    def reverse(self):
        """Reverse Seq"""

        # Transaction
        def atomic_reverse(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Read
            seq = pipe.get(self._redis_key)

            # Reverse
            rev = seq[::-1]

            # Write
            pipe.multi()
            pipe.set(self._redis_key, rev)

        # Execute Transaction
        self._driver.transaction(atomic_reverse, self._redis_key)


    def extend(self, seq):
        """Append Seq wuth another Seq"""

        # Validate Input
        seq = str(seq)

        # Transaction
        def atomic_extend(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Extend
            pipe.multi()
            pipe.append(self._redis_key, seq)

        # Execute Transaction
        if len(seq):
            self._driver.transaction(atomic_extend, self._redis_key)
        else:
            pass

    def pop(self, pop_idx=None):
        """Pop Seq Item"""

        # Transaction
        def atomic_pop(pipe):

            # Check Exists
            if not self._exists(pipe):
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
        ret = self._driver.transaction(atomic_pop, self._redis_key)
        return str(ret[0])

    def remove(self, itm):
        """Remove itm from Seq"""

        # Validate Input
        itm = str(itm)
        if len(itm) != 1:
            raise ValueError("{:s} must be a single charecter".format(itm))

        # Transaction
        def atomic_remove(pipe):

            # Check Exists
            if not self._exists(pipe):
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
        self._driver.transaction(atomic_remove, self._redis_key)

class List(Sequence,
           base_redis.List, atomic_abc.List):
    pass

class MutableList(MutableSequence, List, atomic_abc.MutableList):

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

    def append(self, itm):
        """Append Seq Item"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in seq".format(type(itm)))

        # Transaction
        def atomic_append(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Append
            pipe.multi()
            pipe.rpush(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(atomic_append, self._redis_key)

    def reverse(self):
        """Reverse Seq"""

        # Transaction
        def atomic_reverse(pipe):

            # Check Exists
            if not self._exists(pipe):
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
        self._driver.transaction(atomic_reverse, self._redis_key)

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
        def atomic_extend(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Extend
            pipe.multi()
            pipe.rpush(self._redis_key, *seq)

        # Execute Transaction
        if len(seq):
            self._driver.transaction(atomic_extend, self._redis_key)
        else:
            pass

    def pop(self, pop_idx=None):
        """Pop Seq Item"""

        # Transaction
        def atomic_pop(pipe):

            # Check Exists
            if not self._exists(pipe):
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
        ret = self._driver.transaction(atomic_pop, self._redis_key)
        return str(ret[0][0])

    def remove(self, itm):
        """Remove itm from Seq"""

        # Validate Input
        if (type(itm) is str):
            pass
        else:
            raise TypeError("{} not supported in seq".format(type(itm)))

        # Transaction
        def atomic_remove(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Write
            pipe.multi()
            pipe.lrem(self._redis_key, 1, itm)

        # Execute Transaction
        ret = self._driver.transaction(atomic_remove, self._redis_key)

        # Check result
        if (ret[0] != 1):
            raise ValueError("'{}' is not in list".format(itm))

class Set(BaseSet, base_redis.Set, atomic_abc.Set):
    pass

class MutableSet(MutableBaseSet, Set, atomic_abc.MutableSet):

    def add(self, itm):
        """Add Item to Set"""

        # Validate Input
        if (type(itm) is not str):
            raise TypeError("{} not supported in set".format(type(itm)))

        # Transaction
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
        if (type(itm) is not str):
            raise TypeError("{} not supported in set".format(type(itm)))

        # Transaction
        def atomic_discard(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.srem(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(atomic_discard, self._redis_key)

    def clear(self):
        """Clear Set"""

        # Transaction
        def atomic_clear(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.delete(self._redis_key)

        # Execute Transaction
        self._driver.transaction(atomic_clear, self._redis_key)

    def pop(self):
        """Pop item from Set"""

        # Transaction
        def atomic_pop(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.spop(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_pop, self._redis_key)

        # Check and Return
        if ret[0] is None:
            raise KeyError("Empty set, can not pop()")
        else:
            return ret[0]

    def remove(self, itm):
        """Remove itm from Set"""

        # Transaction
        def atomic_remove(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Check Item in Set
            if not pipe.sismember(self._redis_key, itm):
                raise KeyError("{} not in set".format(itm))

            # Remove Item
            pipe.multi()
            pipe.srem(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(atomic_remove, self._redis_key)

    def __ior__(self, other):
        """Unary or"""

        # Validate Input
        other = set(other)

        # Transaction
        def atomic_ior(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Union Sets
            val = pipe.smembers(self._redis_key)
            val |= other
            pipe.multi()
            if len(val) > 0:
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_ior, self._redis_key)

        # Return
        return self

    def __iand__(self, other):
        """Unary and"""

        # Validate Input
        other = set(other)

        # Transaction
        def atomic_iand(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Intersect Sets
            val = pipe.smembers(self._redis_key)
            val &= other
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_iand, self._redis_key)

        # Return
        return self

    def __ixor__(self, other):
        """Unary xor"""

        # Validate Input
        other = set(other)

        # Transaction
        def atomic_ixor(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Xor Sets
            val = pipe.smembers(self._redis_key)
            val ^= other
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_ixor, self._redis_key)

        # Return
        return self

    def __isub__(self, other):
        """Unary subtract"""

        # Validate Input
        other = set(other)

        # Transaction
        def atomic_isub(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Difference Sets
            val = pipe.smembers(self._redis_key)
            val -= other
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(atomic_isub, self._redis_key)

        # Return
        return self

class Dictionary(Mapping, base_redis.Dictionary, atomic_abc.Dictionary):
    pass

class MutableDictionary(MutableMapping, Dictionary, atomic_abc.MutableDictionary):

    def __setitem__(self, key, val):
        """Set Mapping Item"""

        # Validate Input
        if type(val) is not str:
            raise TypeError("{} not supported in mapping".format(type(val)))

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

        # Transaction
        def atomic_delitem(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Set Item
            pipe.multi()
            pipe.hdel(self._redis_key, key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_delitem, self._redis_key)

        # Validate Return
        if not ret[0]:
            raise KeyError("'{}' not in dict".format(key))

    def pop(self, *args):
        """Pop Specified Item or Default"""

        # Validate input:
        if (len(args) < 1) or (len(args) > 2):
            raise TypeError("pop() requires either 1 or 2 args: {}".format(args))
        key = args[0]

        # Transaction
        def atomic_pop(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Pop Item
            pipe.multi()
            pipe.hget(self._redis_key, key)
            pipe.hdel(self._redis_key, key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_pop, self._redis_key)

        # Process Return
        if not ret[1]:
            if len(args) > 1:
                return args[1]
            else:
                raise KeyError("'{}' not in dict".format(key))
        else:
            return ret[0]

    def popitem(self):
        """Pop Arbitrary Item"""

        # Transaction
        def atomic_popitem(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Set Item
            dic = pipe.hgetall(self._redis_key)
            key, val = dic.popitem()
            pipe.multi()
            pipe.echo(key)
            pipe.echo(val)
            pipe.hdel(self._redis_key, key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_popitem, self._redis_key)

        # Process Return
        key = ret[0]
        val = ret[1]
        assert ret[2] == 1
        return (key, val)

    def clear(self):
        """Clear Dictionary"""

        # Transaction
        def atomic_clear(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.delete(self._redis_key)

        # Execute Transaction
        self._driver.transaction(atomic_clear, self._redis_key)

    def update(self, *args, **kwargs):
        """Update Dictionary"""

        # TODO: Verify input types

        # Transaction
        def atomic_update(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Difference Sets
            val = pipe.hgetall(self._redis_key)
            val.update(*args, **kwargs)
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.hmset(self._redis_key, val)

        # Execute Transaction
        self._driver.transaction(atomic_update, self._redis_key)

        # Return
        return self

    def setdefault(self, key, default=None):
        """return Key or Set to Default"""

        # Transaction
        def atomic_setdefault(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Validate Input
            if not pipe.hexists(self._redis_key, key):
                if type(default) is not str:
                    raise TypeError("{} not supported in mapping".format(type(default)))

            # Set val if not set
            pipe.multi()
            pipe.hsetnx(self._redis_key, key, default)
            pipe.hget(self._redis_key, key)

        # Execute Transaction
        ret = self._driver.transaction(atomic_setdefault, self._redis_key)

        # Return
        return ret[1]
