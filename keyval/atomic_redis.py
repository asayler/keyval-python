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
