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
        def automic_setitem(pipe):

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
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Append
            pipe.multi()
            pipe.append(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(automic_append, self._redis_key)

    def reverse(self):
        """Reverse Seq"""

        # Transaction
        def automic_reverse(pipe):

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
        self._driver.transaction(automic_reverse, self._redis_key)


    def extend(self, seq):
        """Append Seq wuth another Seq"""

        # Validate Input
        seq = str(seq)

        # Transaction
        def automic_extend(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Extend
            pipe.multi()
            pipe.append(self._redis_key, seq)

        # Execute Transaction
        if len(seq):
            self._driver.transaction(automic_extend, self._redis_key)
        else:
            pass

    def pop(self, pop_idx=None):
        """Pop Seq Item"""

        # Transaction
        def automic_pop(pipe):

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
        self._driver.transaction(automic_remove, self._redis_key)

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
        def automic_setitem(pipe):

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
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Append
            pipe.multi()
            pipe.rpush(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(automic_append, self._redis_key)

    def reverse(self):
        """Reverse Seq"""

        # Transaction
        def automic_reverse(pipe):

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
        self._driver.transaction(automic_reverse, self._redis_key)

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
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Extend
            pipe.multi()
            pipe.rpush(self._redis_key, *seq)

        # Execute Transaction
        if len(seq):
            self._driver.transaction(automic_extend, self._redis_key)
        else:
            pass

    def pop(self, pop_idx=None):
        """Pop Seq Item"""

        # Transaction
        def automic_pop(pipe):

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
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Write
            pipe.multi()
            pipe.lrem(self._redis_key, 1, itm)

        # Execute Transaction
        ret = self._driver.transaction(automic_remove, self._redis_key)

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
        def automic_add(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Add Item
            pipe.multi()
            pipe.sadd(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(automic_add, self._redis_key)

    def discard(self, itm):
        """Remove Item from Set if Present"""

        # Validate Input
        if (type(itm) is not str):
            raise TypeError("{} not supported in set".format(type(itm)))

        # Transaction
        def automic_discard(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.srem(self._redis_key, itm)

        # Execute Transaction
        self._driver.transaction(automic_discard, self._redis_key)

    def clear(self):
        """Clear Set"""

        # Transaction
        def automic_clear(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.delete(self._redis_key)

        # Execute Transaction
        self._driver.transaction(automic_clear, self._redis_key)

    def pop(self):
        """Pop item from Set"""

        # Transaction
        def automic_pop(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.spop(self._redis_key)

        # Execute Transaction
        ret = self._driver.transaction(automic_pop, self._redis_key)

        # Check and Return
        if ret[0] is None:
            raise KeyError("Empty set, can not pop()")
        else:
            return ret[0]

    def remove(self, itm):
        """Remove itm from Set"""

        # Transaction
        def automic_remove(pipe):

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
        self._driver.transaction(automic_remove, self._redis_key)

    def __ior__(self, other):
        """Unary or"""

        # Validate Input
        other = set(other)

        # Transaction
        def automic_ior(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Union Items
            val = pipe.smembers(self._redis_key)
            val |= other
            pipe.multi()
            if len(val) > 0:
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(automic_ior, self._redis_key)

        # Return
        return self

    def __iand__(self, other):
        """Unary and"""

        other = set(other)

        # Transaction
        def automic_iand(pipe):

            # Check Exists
            if not self._exists(pipe):
                raise base.ObjectDNE(self)

            # Add Items
            val = pipe.smembers(self._redis_key)
            val &= other
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(val) > 0:
                pipe.sadd(self._redis_key, *val)

        # Execute Transaction
        self._driver.transaction(automic_iand, self._redis_key)

        # Return
        return self
