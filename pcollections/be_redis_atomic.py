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

from . import exceptions
from . import be_redis_base
from . import abc_atomic


### Objects ###

class String(be_redis_base.String):
    pass

class MutableString(String, abc_atomic.MutableString):

    def __setitem__(self, idx, itm):
        """Set Seq Item"""

        # Check Input
        itm = self._encode_val_item(itm, test=True)
        if len(itm) != 1:
            raise ValueError("'{:s}' must be a single charecter".format(itm))

        # Transaction
        def atomic_setitem(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

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
            out = self._encode_val_item(itm)
            pipe.multi()
            pipe.setrange(self._redis_key, idx_norm, out)

        # Execute Transaction
        self._transact(atomic_setitem)

    def insert(self, idx, itm):
        """Insert Seq Item"""

        # Validate Input
        itm = self._encode_val_item(itm, test=True)
        if len(itm) != 1:
            raise ValueError("'{:s}' must be a single charecter".format(itm))

        # Transaction
        def atomic_insert(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Get Ranges
            length = pipe.strlen(self._redis_key)
            if (idx == 0) or (idx <= -length):
                start = str()
            else:
                start = self._decode_val_obj(pipe.getrange(self._redis_key, 0, (idx-1)))
            if (idx >= length):
                end = str()
            else:
                end = self._decode_val_obj(pipe.getrange(self._redis_key, idx, length))

            # Set New Val
            out = self._encode_val_obj(start + itm + end)
            pipe.multi()
            pipe.set(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_insert)

    def append(self, itm):
        """Append Seq Item"""

        # Validate Input
        itm = self._encode_val_item(itm, test=True)
        if len(itm) != 1:
            raise ValueError("'{:s}' must be a single charecter".format(itm))

        # Transaction
        def atomic_append(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Append
            out = self._encode_val_item(itm)
            pipe.multi()
            pipe.append(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_append)

    def reverse(self):
        """Reverse Seq"""

        # Transaction
        def atomic_reverse(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Read
            val = self._decode_val_obj(pipe.get(self._redis_key))

            # Reverse
            rev = val[::-1]

            # Write
            out = self._encode_val_obj(rev)
            pipe.multi()
            pipe.set(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_reverse)

    def extend(self, seq):
        """Append Seq with another Seq"""

        # Validate Input
        seq = self._encode_val_obj(seq, test=True)

        # Transaction
        def atomic_extend(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Extend
            out = self._encode_val_obj(seq)
            pipe.multi()
            pipe.append(self._redis_key, out)

        # Execute Transaction
        if len(seq):
            self._transact(atomic_extend)
        else:
            pass

    def pop(self, pop_idx=None):
        """Pop Seq Item"""

        # Transaction
        def atomic_pop(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

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
                start = str()
            else:
                start = self._decode_val_obj(pipe.getrange(self._redis_key,
                                                           0, (idx-1)))
            if (idx == (length-1)) or (idx == -1):
                end = str()
            else:
                end = self._decode_val_obj(pipe.getrange(self._redis_key,
                                                         (idx+1), length))

            # Set New Val
            out = self._encode_val_obj(start + end)
            pipe.multi()
            pipe.getrange(self._redis_key, idx, idx)
            pipe.set(self._redis_key, out)

        # Execute Transaction
        ret = self._transact(atomic_pop)
        return self._decode_val_item(ret[0])

    def remove(self, itm):
        """Remove itm from Seq"""

        # Validate Input
        itm = self._encode_val_item(itm, test=True)
        if len(itm) != 1:
            raise ValueError("'{:s}' must be a single charecter".format(itm))

        # Transaction
        def atomic_remove(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Get idx
            seq = self._decode_val_obj(pipe.get(self._redis_key))
            idx = seq.index(itm)

            # Get Ranges
            length = pipe.strlen(self._redis_key)
            if (idx == 0):
                start = str()
            else:
                start = self._decode_val_obj(pipe.getrange(self._redis_key, 0, (idx-1)))
            if (idx == (length-1)):
                end = str()
            else:
                end = self._decode_val_obj(pipe.getrange(self._redis_key, (idx+1), length))

            # Set New Val
            out = self._encode_val_obj(start + end)
            pipe.multi()
            pipe.set(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_remove)

class List(be_redis_base.List):
    pass

class MutableList(List, abc_atomic.MutableList):

    def __setitem__(self, idx, itm):
        """Set Seq Item"""

        # Validate Input
        itm = self._encode_val_item(itm, test=True)

        # Transaction
        def atomic_setitem(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

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
            out = self._encode_val_item(itm)
            pipe.multi()
            pipe.lset(self._redis_key, idx_norm, out)

        # Execute Transaction
        self._transact(atomic_setitem)

    def insert(self, idx, itm):
        """Insert Seq Item"""

        # Validate Input
        itm = self._encode_val_item(itm, test=True)

        # Transaction
        def atomic_insert(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Get Ranges
            length = pipe.llen(self._redis_key)
            if (idx == 0) or (idx <= -length):
                start = list()
            else:
                start = self._decode_val_obj(pipe.lrange(self._redis_key, 0, (idx-1)))
            if (idx >= length):
                end = list()
            else:
                end = self._decode_val_obj(pipe.lrange(self._redis_key, idx, length))

            # Set New Val
            out = self._encode_val_obj(start + [itm] + end)
            pipe.multi()
            pipe.delete(self._redis_key)
            pipe.rpush(self._redis_key, *out)

        # Execute Transaction
        self._transact(atomic_insert)

    def append(self, itm):
        """Append Seq Item"""

        # Validate Input
        itm = self._encode_val_item(itm, test=True)

        # Transaction
        def atomic_append(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Append
            out = self._encode_val_item(itm)
            pipe.multi()
            pipe.rpush(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_append)

    def reverse(self):
        """Reverse Seq"""

        # Transaction
        def atomic_reverse(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Read
            seq = self._decode_val_obj(pipe.lrange(self._redis_key, 0, -1))

            # Reverse
            rev = seq[::-1]

            # Write
            out = self._encode_val_obj(rev)
            pipe.multi()
            pipe.delete(self._redis_key)
            pipe.rpush(self._redis_key, *out)

        # Execute Transaction
        self._transact(atomic_reverse)

    def extend(self, seq):
        """Append Seq wuth another Seq"""

        # Validate Input
        seq = self._encode_val_obj(seq, test=True)

        # Transaction
        def atomic_extend(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Extend
            out = self._encode_val_obj(seq)
            pipe.multi()
            pipe.rpush(self._redis_key, *out)

        # Execute Transaction
        if len(seq):
            self._transact(atomic_extend)
        else:
            pass

    def pop(self, pop_idx=None):
        """Pop Seq Item"""

        # Transaction
        def atomic_pop(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

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
                start = list()
            else:
                start = self._decode_val_obj(pipe.lrange(self._redis_key, 0, (idx-1)))
            if (idx == (length-1)) or (idx == -1):
                end = list()
            else:
                end = self._decode_val_obj(pipe.lrange(self._redis_key, (idx+1), length))

            # Set New Val
            out = self._encode_val_obj(start + end)
            pipe.multi()
            pipe.lrange(self._redis_key, idx, idx)
            pipe.delete(self._redis_key)
            pipe.rpush(self._redis_key, *out)

        # Execute Transaction
        ret = self._transact(atomic_pop)
        return self._decode_val_item(ret[0][0])

    def remove(self, itm):
        """Remove itm from Seq"""

        # Validate Input
        itm = self._encode_val_item(itm, test=True)

        # Transaction
        def atomic_remove(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Write
            out = self._encode_val_item(itm)
            pipe.multi()
            pipe.lrem(self._redis_key, 1, out)

        # Execute Transaction
        ret = self._transact(atomic_remove)

        # Check result
        if (ret[0] != 1):
            raise ValueError("'{}' is not in list".format(itm))

class Set(be_redis_base.Set):
    pass

class MutableSet(Set, abc_atomic.MutableSet):

    def add(self, itm):
        """Add Item to Set"""

        # Validate Input
        self._encode_val_item(itm, test=True)

        # Transaction
        def atomic_add(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Add Item
            out = self._encode_val_item(itm)
            pipe.multi()
            pipe.sadd(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_add)

    def discard(self, itm):
        """Remove Item from Set if Present"""

        # Validate Input
        self._encode_val_item(itm, test=True)

        # Transaction
        def atomic_discard(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Remove Item
            out = self._encode_val_item(itm)
            pipe.multi()
            pipe.srem(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_discard)

    def clear(self):
        """Clear Set"""

        # Transaction
        def atomic_clear(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.delete(self._redis_key)

        # Execute Transaction
        self._transact(atomic_clear)

    def pop(self):
        """Pop item from Set"""

        # Transaction
        def atomic_pop(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.spop(self._redis_key)

        # Execute Transaction
        ret = self._transact(atomic_pop)

        # Check and Return
        if ret[0] is None:
            raise KeyError("Empty set, can not pop()")
        else:
            return self._decode_val_item(ret[0])

    def remove(self, itm):
        """Remove itm from Set"""

        # Validate Input
        self._encode_val_item(itm, test=True)

        # Transaction
        def atomic_remove(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Check Item in Set
            out = self._encode_val_item(itm)
            if not pipe.sismember(self._redis_key, out):
                raise KeyError("{} not in set".format(itm))

            # Remove Item
            pipe.multi()
            pipe.srem(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_remove)

    def __ior__(self, other):
        """Unary or"""

        # Validate Input
        other = self._encode_val_obj(other, test=True)

        # Transaction
        def atomic_ior(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Union Sets
            val = self._decode_val_obj(pipe.smembers(self._redis_key))
            val |= other
            out = self._encode_val_obj(val)
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(out) > 0:
                pipe.sadd(self._redis_key, *out)

        # Execute Transaction
        self._transact(atomic_ior)

        # Return
        return self

    def __iand__(self, other):
        """Unary and"""

        # Validate Input
        other = self._encode_val_obj(other, test=True)

        # Transaction
        def atomic_iand(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Intersect Sets
            val = self._decode_val_obj(pipe.smembers(self._redis_key))
            val &= other
            out = self._encode_val_obj(val)
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(out) > 0:
                pipe.sadd(self._redis_key, *out)

        # Execute Transaction
        self._transact(atomic_iand)

        # Return
        return self

    def __ixor__(self, other):
        """Unary xor"""

        # Validate Input
        other = self._encode_val_obj(other, test=True)

        # Transaction
        def atomic_ixor(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Xor Sets
            val = self._decode_val_obj(pipe.smembers(self._redis_key))
            val ^= other
            out = self._encode_val_obj(val)
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(out) > 0:
                pipe.sadd(self._redis_key, *out)

        # Execute Transaction
        self._transact(atomic_ixor)

        # Return
        return self

    def __isub__(self, other):
        """Unary subtract"""

        # Validate Input
        other = self._encode_val_obj(other, test=True)

        # Transaction
        def atomic_isub(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Difference Sets
            val = self._decode_val_obj(pipe.smembers(self._redis_key))
            val -= other
            out = self._encode_val_obj(val)
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(out) > 0:
                pipe.sadd(self._redis_key, *out)

        # Execute Transaction
        self._transact(atomic_isub)

        # Return
        return self

class Dictionary(be_redis_base.Dictionary):
    pass

class MutableDictionary(Dictionary, abc_atomic.MutableDictionary):

    def __setitem__(self, key, val):
        """Set Mapping Item"""

        # Validate Input
        self._encode_val_item(key, test=True)
        self._encode_val_item(val, test=True)

        # Transaction
        def atomic_setitem(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Set Item
            key_out = self._encode_val_item(key)
            val_out = self._encode_val_item(val)
            pipe.multi()
            pipe.hset(self._redis_key, key_out, val_out)

        # Execute Transaction
        self._transact(atomic_setitem)

    def __delitem__(self, key):
        """Delete Mapping Item"""

        # Validate Input
        self._encode_val_item(key, test=True)

        # Transaction
        def atomic_delitem(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Set Item
            key_out = self._encode_val_item(key)
            pipe.multi()
            pipe.hdel(self._redis_key, key_out)

        # Execute Transaction
        ret = self._transact(atomic_delitem)

        # Validate Return
        if not ret[0]:
            raise KeyError("'{}' not in dict".format(key))

    def pop(self, *args):
        """Pop Specified Item or Default"""

        # Validate input:
        if (len(args) < 1) or (len(args) > 2):
            raise TypeError("pop() requires either 1 or 2 args: {}".format(args))
        self._encode_val_item(args[0], test=True)
        key = args[0]
        if len(args) > 1:
            default = args[1]

        # Transaction
        def atomic_pop(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Pop Item
            key_out = self._encode_val_item(key)
            pipe.multi()
            pipe.hget(self._redis_key, key_out)
            pipe.hdel(self._redis_key, key_out)

        # Execute Transaction
        ret = self._transact(atomic_pop)

        # Process Return
        if not ret[1]:
            if len(args) > 1:
                return default
            else:
                raise KeyError("'{}' not in dict".format(key))
        else:
            return self._decode_val_item(ret[0])

    def popitem(self):
        """Pop Arbitrary Item"""

        # Transaction
        def atomic_popitem(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Set Item
            dic = self._decode_val_obj(pipe.hgetall(self._redis_key))
            key, val = dic.popitem()
            key_out = self._encode_val_item(key)
            val_out = self._encode_val_item(val)
            pipe.multi()
            pipe.echo(key_out)
            pipe.echo(val_out)
            pipe.hdel(self._redis_key, key_out)

        # Execute Transaction
        ret = self._transact(atomic_popitem)

        # Process Return
        key_ret = self._decode_val_item(ret[0])
        val_ret = self._decode_val_item(ret[1])
        assert ret[2] == 1
        return (key_ret, val_ret)

    def clear(self):
        """Clear Dictionary"""

        # Transaction
        def atomic_clear(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Remove Item
            pipe.multi()
            pipe.delete(self._redis_key)

        # Execute Transaction
        self._transact(atomic_clear)

    def update(self, *args, **kwargs):
        """Update Dictionary"""

        # TODO: Verify input types

        # Transaction
        def atomic_update(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Difference Sets
            val = self._decode_val_obj(pipe.hgetall(self._redis_key))
            val.update(*args, **kwargs)
            out = self._encode_val_obj(val)
            pipe.multi()
            pipe.delete(self._redis_key)
            if len(out) > 0:
                pipe.hmset(self._redis_key, out)

        # Execute Transaction
        self._transact(atomic_update)

        # Return
        return self

    def setdefault(self, key, default=None):
        """return Key or Set to Default"""

        # Validate Input
        self._encode_val_item(key, test=True)
        if default is not None:
            self._encode_val_item(default, test=True)

        # Transaction
        def atomic_setdefault(pipe):

            # Check Exists
            if not self._exists_direct(pipe):
                raise exceptions.ObjectDNE(self)

            # Validate Input
            key_out = self._encode_val_item(key)
            if not pipe.hexists(self._redis_key, key_out):
                default_out = self._encode_val_item(default)
            else:
                default_out = None

            # Set val if not set
            pipe.multi()
            pipe.hsetnx(self._redis_key, key_out, default_out)
            pipe.hget(self._redis_key, key_out)

        # Execute Transaction
        ret = self._transact(atomic_setdefault)

        # Return
        return self._decode_val_item(ret[1])
