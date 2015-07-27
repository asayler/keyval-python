# -*- coding: utf-8 -*-


# Andy Sayler
# Summer 2014
# Univerity of Colorado


### Imports ###

## stdlib ##
import copy
import collections
import unittest
import warnings

### keyval ###
import keyval.keyval


### Globals ###

_TEST_KEY_PRE = "TESTKEY"

### Initialization ###

warnings.simplefilter('default')


### Exceptions ###

class BaseTestError(Exception):
    """Base class for BaseTest Exceptions"""

    def __init__(self, *args, **kwargs):
        super(BaseTestError, self).__init__(*args, **kwargs)

### Base Class ###

class BaseTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.key_cnt = 0
        self.val_cnt = 0

    def tearDown(self):
        super(BaseTestCase, self).tearDown()

    def generate_key(self):
        key = "{:s}_{:d}".format(_TEST_KEY_PRE, self.key_cnt)
        self.key_cnt += 1
        return key

### Base Mixins ###

class PersistentMixin(object):

    def helper_raises(self, size, error, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.helper_raises_core(instance, val, error, test_func, *args)
        instance.rem()

    def helper_raises_core(self, instance, ref, error, test_func, *args):

        self.assertEqual(ref, instance.get_val())
        self.assertRaises(error, test_func, instance, *args)

    def helper_dne(self, test_func, *args):

        key = self.generate_key()
        instance = self.factory.from_raw(key)
        self.helper_dne_core(instance, test_func, *args)

    def helper_dne_core(self, instance, test_func, *args):

        self.assertFalse(instance.exists())
        self.assertRaises(keyval.keyval.ObjectDNE, test_func, instance, *args)

    def helper_ab_immutable(self, size, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.helper_ab_immutable_core(instance, val, test_func, *args)
        instance.rem()

    def helper_ab_immutable_core(self, instance, ref, test_func, *args):

        self.assertTrue(instance.exists())
        self.assertEqual(ref, instance.get_val())
        orig_ref = copy.copy(ref)
        ref_ret = test_func(ref, *args)
        instance_ret = test_func(instance, *args)
        self.assertEqual(ref_ret, instance_ret)
        self.assertEqual(orig_ref, instance.get_val())
        self.assertEqual(orig_ref, ref)

    def helper_exp_immutable(self, size, exp_ret, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.helper_exp_immutable_core(instance, val, exp_ret, test_func, *args)
        instance.rem()

    def helper_exp_immutable_core(self, instance, ref, exp_ret, test_func, *args):

        self.assertTrue(instance.exists())
        self.assertEqual(ref, instance.get_val())
        orig_ref = copy.copy(ref)
        ret = test_func(instance, *args)
        self.assertEqual(exp_ret, ret)
        self.assertEqual(orig_ref, instance.get_val())
        self.assertEqual(orig_ref, ref)

    def test_from_new_empty(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(0)
        self.assertEqual(len(val), 0)

        # Create Invalid Instance
        self.assertRaises(TypeError, self.factory.from_new, None, None)
        self.assertRaises(TypeError, self.factory.from_new, None, val)
        self.assertRaises(TypeError, self.factory.from_new, key,  None)

        # Create Valid Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.get_key())
        self.assertEqual(val, instance.get_val())

        # Recreate Instance
        self.assertRaises(keyval.keyval.ObjectExists, self.factory.from_new, key, val)

        # Cleanup
        instance.rem()

    def test_from_new_nonempty(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)
        self.assertGreater(len(val), 0)

        # Create Invalid Instance
        self.assertRaises(TypeError, self.factory.from_new, None, None)
        self.assertRaises(TypeError, self.factory.from_new, None, val)
        self.assertRaises(TypeError, self.factory.from_new, key,  None)

        # Create Valid Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.get_key())
        self.assertEqual(val, instance.get_val())

        # Recreate Instance
        self.assertRaises(keyval.keyval.ObjectExists, self.factory.from_new, key, val)

        # Cleanup
        instance.rem()

    def test_from_existing_empty(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(0)
        self.assertEqual(len(val), 0)

        # Get Invalid Instance
        self.assertRaises(TypeError, self.factory.from_existing, None)

        # Get Nonexistant Instance
        self.assertRaises(keyval.keyval.ObjectDNE, self.factory.from_existing, key)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())

        # Get Existing Instance
        instance = self.factory.from_existing(key)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.get_key())
        self.assertEqual(val, instance.get_val())

        # Cleanup
        instance.rem()

    def test_from_existing_nonempty(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)
        self.assertGreater(len(val), 0)

        # Get Invalid Instance
        self.assertRaises(TypeError, self.factory.from_existing, None)

        # Get Nonexistant Instance
        self.assertRaises(keyval.keyval.ObjectDNE, self.factory.from_existing, key)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())

        # Get Existing Instance
        instance = self.factory.from_existing(key)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.get_key())
        self.assertEqual(val, instance.get_val())

        # Cleanup
        instance.rem()

    def test_from_raw(self):

        # Setup Test Vals
        key = self.generate_key()

        # Get Invalid Instance
        self.assertRaises(TypeError, self.factory.from_raw, None)

        # Get Raw Instance
        instance = self.factory.from_raw(key)
        self.assertFalse(instance.exists())
        self.assertEqual(key, instance.get_key())
        self.assertRaises(keyval.keyval.ObjectDNE, instance.get_val)

    def test_rem(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())

        # Remove Instance
        instance.rem()
        self.assertFalse(instance.exists())

        # Rem Non-existant Instance (No Force)
        self.assertRaises(keyval.keyval.ObjectDNE, instance.rem)

        # Rem Non-existant Instance (Force)
        instance.rem(force=True)
        self.assertFalse(instance.exists())

    def test_get_val(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(val, instance.get_val())

        # Rem Instance
        instance.rem()
        self.assertRaises(keyval.keyval.ObjectDNE, instance.get_val)

    def test_get_key(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(key, instance.get_key())

        # Rem Instance
        instance.rem()
        self.assertEqual(key, instance.get_key())

    def test_unicode(self):

        # Test DNE
        self.helper_dne(unicode)

        # Test Good
        self.helper_ab_immutable(10, unicode)

    def test_string(self):

        # Test DNE
        self.helper_dne(str)

        # Test Good
        self.helper_ab_immutable(10, str)

    def test_bool(self):

        # Test DNE
        self.helper_dne(bool)

        # Test Good
        self.helper_ab_immutable( 0, bool)
        self.helper_ab_immutable( 1, bool)
        self.helper_ab_immutable(10, bool)

    def test_repr(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(key, repr(instance))

        # Cleanup
        instance.rem()

class MutableMixin(PersistentMixin):

    def helper_ab_mutable(self, size, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.helper_ab_mutable_core(instance, val, test_func, *args)
        instance.rem()

    def helper_ab_mutable_core(self, instance, ref, test_func, *args):

        self.assertTrue(instance.exists())
        self.assertEqual(ref, instance.get_val())
        ref_ret = test_func(ref, *args)
        instance_ret = test_func(instance, *args)
        self.assertEqual(ref_ret, instance_ret)
        self.assertEqual(ref, instance.get_val())

    def helper_exp_mutable(self, size, exp_ret, exp_val, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.helper_exp_mutable_core(instance, val, exp_ret, exp_val, test_func, *args)
        instance.rem()

    def helper_exp_mutable_core(self, instance, ref, exp_ret, exp_val, test_func, *args):

        self.assertTrue(instance.exists())
        self.assertEqual(ref, instance.get_val())
        ret = test_func(instance, *args)
        self.assertEqual(exp_ret, ret)
        self.assertEqual(exp_val, instance.get_val())

    def test_set_val_empty(self):

        def test_func(instance, new_val):
            instance.set_val(new_val)

        # Setup
        new_val = self.generate_val_multi(0)
        self.assertEqual(len(new_val), 0)

        # Test DNE
        self.helper_dne(test_func, new_val)

        # Test Good
        self.helper_exp_mutable(0, None, new_val, test_func, new_val)

        # Test Bad
        self.helper_raises(0, TypeError, test_func, None)

    def test_set_val_nonempty(self):

        def test_func(instance, new_val):
            instance.set_val(new_val)

        # Setup
        new_val = self.generate_val_multi(10)
        self.assertGreater(len(new_val), 0)

        # Test DNE
        self.helper_dne(test_func, new_val)

        # Test Good
        self.helper_exp_mutable(10, None, new_val, test_func, new_val)

        # Test Bad
        self.helper_raises(10, TypeError, test_func, None)

class EqualityMixin(PersistentMixin):

    def test_eq(self):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        val = self.generate_val_multi(10)

        # Create Instance
        instance_a = self.factory.from_new(key_a, val)
        instance_b = self.factory.from_new(key_b, val)
        self.assertEqual(instance_a, instance_b)
        self.assertEqual(instance_b, instance_a)

        # Cleanup
        instance_a.rem()
        instance_b.rem()

    def test_ne(self):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        val_a = self.generate_val_multi(10)
        val_b = self.generate_val_multi(10)
        self.assertNotEqual(val_a, val_b)

        # Create Instance
        instance_a = self.factory.from_new(key_a, val_a)
        instance_b = self.factory.from_new(key_b, val_b)
        self.assertNotEqual(instance_a, instance_b)

        # Cleanup
        instance_a.rem()
        instance_b.rem()

class ComparableMixin(EqualityMixin):

    def helper_cmp(self, mode, func, sorted_vals):

        # Process Args
        if (mode[0] == "l"):
            less = True
            greater = False
        elif (mode[0] == "g"):
            less = False
            greater = True
        else:
            raise Exception("Unknown Mode: {}".format(mode))

        if (mode[1] == "e"):
            equal = True
        elif (mode[1] == "t"):
            equal = False
        else:
            raise Exception("Unknown Mode: {}".format(mode))

        if len(sorted_vals) < 2:
            raise Exception("Need at least two non-dup vals")

        # Setup Test Vals
        instances = []
        for val in sorted_vals:
            key = self.generate_key()
            instance = self.factory.from_new(key, val)
            instances.append(instance)

        # Test Inequality
        for idx_a in range(len(instances)):
            a = instances[idx_a]
            for idx_b in range(len(instances)):
                b = instances[idx_b]
                try:
                    if (idx_a == idx_b):
                        # Test Equilty
                        self.assertEqual(a, b)
                        self.assertEqual(equal, func(a, b))
                        self.assertEqual(equal, func(b, a))
                    else:
                        # Test Inequality
                        self.assertNotEqual(a, b)
                        if (idx_a < idx_b):
                            # Test Less
                            self.assertEqual(less, func(a, b))
                        else:
                            # Test Greater
                            self.assertEqual(greater, func(a, b))
                except AssertionError:
                    print("")
                    print("idx_a = {:d}".format(idx_a))
                    print("idx_b = {:d}".format(idx_b))
                    print("a key = {}".format(a.get_key()))
                    print("a val = {}".format(a.get_val()))
                    print("b key = {}".format(b.get_key()))
                    print("b val = {}".format(b.get_val()))
                    raise

        # Cleanup
        for instance in instances:
            instance.rem()

    def test_lt(self):

        def func_lt(a, b):
            return a < b

        vals = self.generate_vals_sorted(10, 10)
        self.helper_cmp("lt", func_lt, vals)

    def test_le(self):

        def func_le(a, b):
            return a <= b

        vals = self.generate_vals_sorted(10, 10)
        self.helper_cmp("le", func_le, vals)

    def test_gt(self):

        def func_gt(a, b):
            return a > b

        vals = self.generate_vals_sorted(10, 10)
        self.helper_cmp("gt", func_gt, vals)

    def test_ge(self):

        def func_ge(a, b):
            return a >= b

        vals = self.generate_vals_sorted(10, 10)
        self.helper_cmp("ge", func_ge, vals)

class ContainerMixin(PersistentMixin):

    def test_contains(self):

        def contains(instance, item):
            return item in instance

        # Test DNE
        self.helper_dne(contains, None)

        # Test In
        def contains_in(instance):
            item = next(iter(instance))
            return contains(instance, item)
        self.helper_ab_immutable(10, contains_in)

        # Test Out
        def contains_out(instance):
            item = self.generate_val_single(exclude=instance)
            return contains(instance, item)
        self.helper_ab_immutable(10, contains_out)

class IterableMixin(PersistentMixin):

    def test_iter(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create Instance
        instance = self.factory.from_new(key, val)

        # Test Instance
        for i in instance:
            self.assertTrue(i in val)

        # Cleanup
        instance.rem()

class SizedMixin(PersistentMixin):

    def test_len(self):

        # Test DNE
        self.helper_dne(len)

        # Test Good
        self.helper_ab_immutable( 0, len)
        self.helper_ab_immutable( 1, len)
        self.helper_ab_immutable(10, len)

    def test_empty(self):

        # Test Len
        self.helper_ab_immutable( 0, len)

        # Test Bool
        self.helper_ab_immutable( 0, bool)

class SequenceMixin(ContainerMixin, IterableMixin, SizedMixin):

    def test_getitem(self):

        def getitem(instance, index):
            return instance[index]

        # Test DNE
        self.helper_dne(getitem, None)

        # Test Good
        for i in range(10):
            self.helper_ab_immutable(10, getitem,  i    )
            self.helper_ab_immutable(10, getitem, (i-10))

        # Test OOB
        self.helper_raises( 1, IndexError, getitem,   1)
        self.helper_raises( 1, IndexError, getitem,  -2)
        self.helper_raises(10, IndexError, getitem,  10)
        self.helper_raises(10, IndexError, getitem,  11)
        self.helper_raises(10, IndexError, getitem, -11)
        self.helper_raises(10, IndexError, getitem, -12)

    def test_index(self):

        def index(instance, item):
            return instance.index(item)

        # Test DNE
        self.helper_dne(index, None)

        # Test In
        def index_in(instance, idx):
            item = instance[idx]
            return index(instance, item)
        for i in range(10):
            self.helper_ab_immutable(10, index_in,  i    )
            self.helper_ab_immutable(10, index_in, (i-10))

        # Test Out
        def index_out(instance):
            item = self.generate_val_single(exclude=instance)
            return index(instance, item)
        self.helper_raises(10, ValueError, index_out)

    def test_count(self):

        def count(instance, item):
            return instance.count(item)

        # Test DNE
        self.helper_dne(count, None)

        # Test In
        def count_in(instance, index):
            item = instance[index]
            return count(instance, item)
        for i in range(10):
            self.helper_ab_immutable(10, count_in,  i)
            self.helper_ab_immutable(10, count_in, (i-10))

        # Test Out
        def count_out(instance):
            item = self.generate_val_single(exclude=instance)
            return count(instance, item)
        self.helper_ab_immutable(10, count_out)

    def test_reversed(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create Instance
        instance = self.factory.from_new(key, val)

        # Test Instance
        cnt = -1
        for i in reversed(instance):
            self.assertEqual(val[cnt], i)
            cnt -= 1

        # Cleanup
        instance.rem()

    def test_empty(self):

        # Call Parent
        super(SequenceMixin, self).test_empty()

        # Test getitem
        def getitem(instance, index):
            return instance[index]
        self.helper_raises( 0, IndexError, getitem,  0)
        self.helper_raises( 0, IndexError, getitem,  1)
        self.helper_raises( 0, IndexError, getitem, -1)

class MutableSequenceMixin(SequenceMixin, MutableMixin):

    def test_setitem(self):

        def setitem(instance, idx, item):
            instance[idx] = item

        # Test DNE
        item = self.generate_val_single()
        self.helper_dne(setitem, None, item)

        # Test Good
        for i in range(10):
            item = self.generate_val_single()
            self.helper_ab_mutable(10, setitem,  i,     item)
            item = self.generate_val_single()
            self.helper_ab_mutable(10, setitem, (i-10), item)

        # Test OOB
        item = self.generate_val_single()
        self.helper_raises( 1, IndexError, setitem,   1, item)
        self.helper_raises( 1, IndexError, setitem,  -2, item)
        self.helper_raises(10, IndexError, setitem,  10, item)
        self.helper_raises(10, IndexError, setitem,  11, item)
        self.helper_raises(10, IndexError, setitem, -11, item)
        self.helper_raises(10, IndexError, setitem, -12, item)

    def test_delitem(self):

        def delitem(instance, idx):
            del(instance[idx])

        # Test DNE
        self.helper_dne(delitem, None)

        # Test Good
        for i in range(10):
            self.helper_ab_mutable(10, delitem,  i)
            self.helper_ab_mutable(10, delitem, (i-10))

        # Test OOB
        self.helper_raises(10, IndexError, delitem,  10)
        self.helper_raises(10, IndexError, delitem,  11)
        self.helper_raises(10, IndexError, delitem, -11)
        self.helper_raises(10, IndexError, delitem, -12)

    def test_insert(self):

        def insert(instance, idx, item):
            return instance.insert(idx, item)

        # Test DNE
        item = self.generate_val_single()
        self.helper_dne(insert, None, item)

        # Test Inside
        for i in range(10):
            item = self.generate_val_single()
            self.helper_ab_mutable(10, insert,  i,     item)
            item = self.generate_val_single()
            self.helper_ab_mutable(10, insert, (i-10), item)

        # Test Before
        item = self.generate_val_single()
        self.helper_ab_mutable(10, insert, -11, item)
        self.helper_ab_mutable(10, insert, -12, item)

        # Test After
        item = self.generate_val_single()
        self.helper_ab_mutable(10, insert, 10, item)
        self.helper_ab_mutable(10, insert, 11, item)

    def test_append(self):

        def append(instance, itm):
            return instance.append(itm)

        # Test DNE
        itm = self.generate_val_single()
        self.helper_dne(append, itm)

        # Test Append
        itm = self.generate_val_single()
        self.helper_ab_mutable(10, append, itm)
        itm = self.generate_val_single()
        self.helper_ab_mutable(10, append, itm)

    def test_extend(self):

        def extend(instance, seq):
            return instance.extend(seq)

        # Test DNE
        seq = self.generate_val_multi(1)
        self.helper_dne(extend, seq)

        # Test Single
        itm = self.generate_val_single()
        self.helper_ab_mutable(10, extend, itm)

        # Test Seq
        for cnt in range(5):
            seq = self.generate_val_multi(cnt)
            self.helper_ab_mutable(10, extend, seq)

    def test_reverse(self):

        def reverse(instance):
            return instance.reverse()

        # Test DNE
        self.helper_dne(reverse)

        # Test Reverse
        for cnt in range(1, 5):
            self.helper_ab_mutable(cnt, reverse)

    def test_pop(self):

        def pop(instance, idx=None):
            if idx is None:
                ret = instance.pop()
            else:
                ret = instance.pop(idx)
            return ret

        # Test DNE
        self.helper_dne(pop)
        self.helper_dne(pop, 0)

        # Test Pop
        self.helper_ab_mutable(10, pop)
        for idx in range(10):
            self.helper_ab_mutable(10, pop, idx)

        #TODO - Add pop from empty set test for KeyError

    def test_remove(self):

        def remove(instance, itm):
            return instance.remove(itm)

        # Test DNE
        itm = self.generate_val_single()
        self.helper_dne(remove, itm)

        # Test In
        def remove_in(instance, idx):
            itm = instance[idx]
            return remove(instance, itm)
        for i in range(10):
            self.helper_ab_mutable(10, remove_in,  i    )

        # Test Out
        def remove_out(instance):
            itm = self.generate_val_single(exclude=instance)
            return remove(instance, itm)
        self.helper_raises(10, ValueError, remove_out)

    def test_iadd(self):

        def iadd(instance, other):
            instance += other
            self.assertIsNotNone(instance)

        # Test DNE
        seq = self.generate_val_multi(1)
        self.helper_dne(iadd, seq)

        # Test Single
        itm = self.generate_val_single()
        self.helper_ab_mutable(10, iadd, itm)

        # Test Seq
        for cnt in range(5):
            seq = self.generate_val_multi(cnt)
            self.helper_ab_mutable(10, iadd, seq)

class BaseSetMixin(ComparableMixin, ContainerMixin, IterableMixin, SizedMixin):

    def test_issubset(self):

        def func_issubset(a, b):
            return a.issubset(b)

        vals = self.generate_vals_sorted(None, 10)
        self.helper_cmp("le", func_issubset, vals)

    def test_issuperset(self):

        def func_issuperset(a, b):
            return a.issuperset(b)

        vals = self.generate_vals_sorted(None, 10)
        self.helper_cmp("ge", func_issuperset, vals)

    def helper_and(self, func):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        key_c = self.generate_key()
        val_a = set(['a', 'b'])
        val_b = set(['b', 'c'])
        val_c = set(['c', 'd'])
        set_b = set(['b'])
        set_c = set(['c'])
        set_x = set([])

        # Create Instance
        instance_a = self.factory.from_new(key_a, val_a)
        instance_b = self.factory.from_new(key_b, val_b)
        instance_c = self.factory.from_new(key_c, val_c)
        self.assertEqual(set_b, func(instance_a, instance_b))
        self.assertEqual(set_b, func(instance_b, instance_a))
        self.assertEqual(set_c, func(instance_b, instance_c))
        self.assertEqual(set_c, func(instance_c, instance_b))
        self.assertEqual(set_x, func(instance_a, instance_c))
        self.assertEqual(set_x, func(instance_c, instance_a))
        self.assertEqual(val_a, func(instance_a, instance_a))
        self.assertEqual(val_b, func(instance_b, instance_b))
        self.assertEqual(val_c, func(instance_c, instance_c))

        # Cleanup
        instance_a.rem()
        instance_b.rem()
        instance_c.rem()

    def test_and(self):

        def func_and(a, b):
            return a & b

        self.helper_and(func_and)

    def test_intersection(self):

        def func_intersection(a, b):
            return a.intersection(b)

        self.helper_and(func_intersection)

    def helper_or(self, func):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        key_c = self.generate_key()
        val_a = set(['a', 'b'])
        val_b = set(['b', 'c'])
        val_c = set(['c', 'd'])
        set_a = set(['a', 'b', 'c'])
        set_b = set(['b', 'c', 'd'])
        set_c = set(['a', 'b', 'c', 'd'])

        # Create Instance
        instance_a = self.factory.from_new(key_a, val_a)
        instance_b = self.factory.from_new(key_b, val_b)
        instance_c = self.factory.from_new(key_c, val_c)
        self.assertEqual(set_a, func(instance_a, instance_b))
        self.assertEqual(set_a, func(instance_b, instance_a))
        self.assertEqual(set_b, func(instance_b, instance_c))
        self.assertEqual(set_b, func(instance_c, instance_b))
        self.assertEqual(set_c, func(instance_a, instance_c))
        self.assertEqual(set_c, func(instance_c, instance_a))
        self.assertEqual(val_a, func(instance_a, instance_a))
        self.assertEqual(val_b, func(instance_b, instance_b))
        self.assertEqual(val_c, func(instance_c, instance_c))

        # Cleanup
        instance_a.rem()
        instance_b.rem()
        instance_c.rem()

    def test_or(self):

        def func_or(a, b):
            return a | b

        self.helper_or(func_or)

    def test_union(self):

        def func_union(a, b):
            return a.union(b)

        self.helper_or(func_union)

    def helper_sub(self, func):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        key_c = self.generate_key()
        val_a = set(['a', 'b'])
        val_b = set(['b', 'c'])
        val_c = set(['a', 'b', 'c'])
        set_a = set(['a'])
        set_c = set(['c'])
        set_x = set([])

        # Create Instance
        instance_a = self.factory.from_new(key_a, val_a)
        instance_b = self.factory.from_new(key_b, val_b)
        instance_c = self.factory.from_new(key_c, val_c)
        self.assertEqual(set_a, func(instance_a, instance_b))
        self.assertEqual(set_c, func(instance_b, instance_a))
        self.assertEqual(set_x, func(instance_a, instance_c))
        self.assertEqual(set_c, func(instance_c, instance_a))
        self.assertEqual(set_x, func(instance_b, instance_c))
        self.assertEqual(set_a, func(instance_c, instance_b))
        self.assertEqual(set_x, func(instance_a, instance_a))
        self.assertEqual(set_x, func(instance_b, instance_b))
        self.assertEqual(set_x, func(instance_c, instance_c))

        # Cleanup
        instance_a.rem()
        instance_b.rem()
        instance_c.rem()

    def test_sub(self):

        def func_sub(a, b):
            return a - b

        self.helper_sub(func_sub)

    def test_difference(self):

        def func_difference(a, b):
            return a.difference(b)

        self.helper_sub(func_difference)

    def helper_xor(self, func):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        key_c = self.generate_key()
        val_a = set(['a', 'b'])
        val_b = set(['b', 'c'])
        val_c = set(['c', 'd'])
        set_a = set(['a', 'c'])
        set_b = set(['b', 'd'])
        set_c = set(['a', 'b', 'c', 'd'])
        set_x = set([])

        # Create Instance
        instance_a = self.factory.from_new(key_a, val_a)
        instance_b = self.factory.from_new(key_b, val_b)
        instance_c = self.factory.from_new(key_c, val_c)
        self.assertEqual(set_a, func(instance_a, instance_b))
        self.assertEqual(set_a, func(instance_b, instance_a))
        self.assertEqual(set_b, func(instance_b, instance_c))
        self.assertEqual(set_b, func(instance_c, instance_b))
        self.assertEqual(set_c, func(instance_a, instance_c))
        self.assertEqual(set_c, func(instance_c, instance_a))
        self.assertEqual(set_x, func(instance_a, instance_a))
        self.assertEqual(set_x, func(instance_b, instance_b))
        self.assertEqual(set_x, func(instance_c, instance_c))

        # Cleanup
        instance_a.rem()
        instance_b.rem()
        instance_c.rem()

    def test_xor(self):

        def func_xor(a, b):
            return a ^ b

        self.helper_xor(func_xor)

    def test_symmetric_difference(self):

        def func_symmetric_difference(a, b):
            return a.symmetric_difference(b)

        self.helper_xor(func_symmetric_difference)

    def test_isdisjoint(self):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        key_c = self.generate_key()
        val_a = set(['a', 'b'])
        val_b = set(['b', 'c'])
        val_c = set(['c', 'd'])

        # Create Instance
        instance_a = self.factory.from_new(key_a, val_a)
        instance_b = self.factory.from_new(key_b, val_b)
        instance_c = self.factory.from_new(key_c, val_c)
        self.assertFalse(instance_a.isdisjoint(instance_b))
        self.assertFalse(instance_b.isdisjoint(instance_a))
        self.assertFalse(instance_b.isdisjoint(instance_c))
        self.assertFalse(instance_c.isdisjoint(instance_b))
        self.assertTrue(instance_a.isdisjoint(instance_c))
        self.assertTrue(instance_c.isdisjoint(instance_a))
        self.assertFalse(instance_a.isdisjoint(instance_a))
        self.assertFalse(instance_b.isdisjoint(instance_b))
        self.assertFalse(instance_c.isdisjoint(instance_c))

        # Cleanup
        instance_a.rem()
        instance_b.rem()
        instance_c.rem()

class MutableBaseSetMixin(MutableMixin, BaseSetMixin):

    def test_add(self):

        def add(instance, itm):
            return instance.add(itm)

        # Test DNE
        itm = self.generate_val_single()
        self.helper_dne(add, itm)

        # Test Bad Itm
        itm = None
        self.helper_raises(10, TypeError, add, itm)

        # Test Add New
        itm = self.generate_val_single()
        self.helper_ab_mutable(10, add, itm)
        itm = self.generate_val_single()
        self.helper_ab_mutable(10, add, itm)

        # Test Add Same
        itm = self.generate_val_single()
        self.helper_ab_mutable(10, add, itm)
        self.helper_ab_mutable(10, add, itm)

    def test_discard(self):

        def discard(instance, itm):
            return instance.discard(itm)

        # Test DNE
        itm = self.generate_val_single()
        self.helper_dne(discard, itm)

        # Test Bad Itm
        itm = None
        self.helper_raises(10, TypeError, discard, itm)

        # Test In
        def discard_in(instance):
            itm = next(iter(instance))
            return discard(instance, itm)
        self.helper_ab_mutable(2, discard_in)
        self.helper_ab_mutable(10, discard_in)

        # Test Out
        def discard_out(instance):
            itm = self.generate_val_single(exclude=instance)
            return discard(instance, itm)
        self.helper_ab_mutable(2, discard_out)
        self.helper_ab_mutable(10, discard_out)

    def test_clear(self):

        def clear(instance):
            instance.clear()

        # Test DNE
        self.helper_dne(clear)

        # Create Instance
        i_key = self.generate_key()
        i_val = set(["a", "b", "c"])
        self.assertGreater(len(i_val), 0)
        instance = self.factory.from_new(i_key, i_val)
        self.assertGreater(len(instance), 0)
        self.assertEqual(instance.get_val(), i_val)

        # Test Full
        clear(instance)
        self.assertEqual(0, len(instance))
        clear(i_val)
        self.assertEqual(0, len(i_val))
        self.assertEqual(instance.get_val(), i_val)

        # Test Empty
        clear(instance)
        self.assertEqual(0, len(instance))
        clear(i_val)
        self.assertEqual(0, len(i_val))
        self.assertEqual(instance.get_val(), i_val)

        # Cleanup
        instance.rem()

    def test_pop(self):

        def pop(instance):
            return instance.pop()

        # Test DNE
        self.helper_dne(pop)

        # Create Instance
        i_key = self.generate_key()
        i_val = set(["a", "b", "c"])
        instance = self.factory.from_new(i_key, i_val)

        while len(instance) > 0:
            i = pop(instance)
            self.assertIn(i, i_val)
            self.assertNotIn(i, instance)
            i_val.remove(i)
        self.assertEqual(0, len(instance))
        self.assertEqual(0, len(i_val))
        self.assertEqual(instance.get_val(), i_val)

        # Test Empty
        self.helper_raises_core(instance, i_val, KeyError, pop)

        # Cleanup
        instance.rem()

    def test_remove(self):

        def remove(instance, item):
            instance.remove(item)

        # Test DNE
        self.helper_dne(remove, "a")

        # Create Instance
        i_key = self.generate_key()
        i_val = set(["a", "b", "c"])
        instance = self.factory.from_new(i_key, i_val)

        # Test Bad Key
        self.helper_raises_core(instance, i_val, KeyError, remove, "d")

        # Test Existing Items
        for i in instance.get_val():
            self.helper_ab_mutable_core(instance, i_val, remove, i)
        self.assertEqual(0, len(instance))
        self.assertEqual(0, len(i_val))

        # Test Empty
        self.helper_raises_core(instance, i_val, KeyError, remove, "a")

        # Cleanup
        instance.rem()

    def test_ior(self):

        # Test Overlap
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set(['b', 'c']))
        instance_a |= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b', 'c']), instance_a.get_val())
        self.assertEqual(set(['b', 'c']) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

        # Test Discreet
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set(['c', 'd']))
        instance_a |= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b', 'c', 'd']), instance_a.get_val())
        self.assertEqual(set(['c', 'd']) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

        # Test Identity
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_a |= instance_a
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b']), instance_a.get_val())
        instance_a.rem()

        # Test Empty
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set([]))
        instance_a |= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b']), instance_a.get_val())
        self.assertEqual(set([]) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

    def test_iand(self):

        # Test Overlap
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set(['b', 'c']))
        instance_a &= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['b']), instance_a.get_val())
        self.assertEqual(set(['b', 'c']) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

        # Test Discreet
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set(['c', 'd']))
        instance_a &= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set([]), instance_a.get_val())
        self.assertEqual(set(['c', 'd']) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

        # Test Identity
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_a &= instance_a
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b']), instance_a.get_val())
        instance_a.rem()

        # Test Empty
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set([]))
        instance_a &= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set([]), instance_a.get_val())
        self.assertEqual(set([]) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

    def test_ixor(self):

        # Test Overlap
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set(['b', 'c']))
        instance_a ^= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'c']), instance_a.get_val())
        self.assertEqual(set(['b', 'c']) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

        # Test Discreet
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set(['c', 'd']))
        instance_a ^= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b', 'c', 'd']), instance_a.get_val())
        self.assertEqual(set(['c', 'd']) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

        # Test Identity
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_a ^= instance_a
        self.assertIsNotNone(instance_a)
        self.assertEqual(set([]), instance_a.get_val())
        instance_a.rem()

        # Test Empty
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set([]))
        instance_a ^= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b']), instance_a.get_val())
        self.assertEqual(set([]) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

    def test_isub(self):

        # Test Overlap
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set(['b', 'c']))
        instance_a -= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a']), instance_a.get_val())
        self.assertEqual(set(['b', 'c']) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

        # Test Discreet
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set(['c', 'd']))
        instance_a -= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b']), instance_a.get_val())
        self.assertEqual(set(['c', 'd']) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

        # Test Identity
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_a -= instance_a
        self.assertIsNotNone(instance_a)
        self.assertEqual(set([]), instance_a.get_val())
        instance_a.rem()

        # Test Empty
        instance_a = self.factory.from_new("key_a", set(['a', 'b']))
        instance_b = self.factory.from_new("key_b", set([]))
        instance_a -= instance_b
        self.assertIsNotNone(instance_a)
        self.assertEqual(set(['a', 'b']), instance_a.get_val())
        self.assertEqual(set([]) ,instance_b.get_val())
        instance_a.rem()
        instance_b.rem()

class MappingMixin(EqualityMixin, ContainerMixin, IterableMixin, SizedMixin):

    def test_getitem(self):

        def getitem(instance, key):
            return instance[key]

        # Test DNE
        self.helper_dne(getitem, None)

        # Create Instance
        i_key = self.generate_key()
        i_val = {"key_a": "val_a", "key_b": "val_b", "key_c": "val_c"}
        instance = self.factory.from_new(i_key, i_val)

        # Test Good Keys
        for k in i_val:
            self.helper_ab_immutable_core(instance, i_val, getitem, k)

        # Test Bad Key
        self.helper_raises_core(instance, i_val, KeyError, getitem, "key_d")

        # Cleanup
        instance.rem()

    def test_get(self):

        def get(instance, key):
            return instance.get(key)
        def get_default(instance, key, default):
            return instance.get(key, default)

        # Test DNE
        self.helper_dne(get, "key_a")
        self.helper_dne(get_default, "key_a", "val_x")

        # Create Instance
        i_key = self.generate_key()
        i_val = {"key_a": "val_a", "key_b": "val_b", "key_c": "val_c"}
        instance = self.factory.from_new(i_key, i_val)

        # Test Bad Key (Full)
        self.helper_ab_immutable_core(instance, i_val, get_default, "key_d", "val_x")
        self.helper_exp_immutable_core(instance, i_val, "val_x", get_default, "key_d", "val_x")
        self.helper_exp_immutable_core(instance, i_val, None, get, "key_d")

        # Test Good Keys
        for k in i_val:
            self.helper_ab_immutable_core(instance, i_val, get, k)
            self.helper_ab_immutable_core(instance, i_val, get_default, k, "val_x")

        # Test Bad Key (Empty)
        self.helper_ab_immutable_core(instance, i_val, get_default, "key_d", "val_x")
        self.helper_exp_immutable_core(instance, i_val, "val_x", get_default, "key_d", "val_x")
        self.helper_exp_immutable_core(instance, i_val, None, get, "key_d")

        # Cleanup
        instance.rem()

    def test_keys(self):

        def keys(instance):
            return instance.keys()

        # Test DNE
        self.helper_dne(keys)

        # Test Keys
        self.helper_ab_immutable(10, keys)

    def test_values(self):

        def values(instance):
            return instance.values()

        # Test DNE
        self.helper_dne(values)

        # Test Values
        self.helper_ab_immutable(10, values)

    def test_items(self):

        def items(instance):
            return instance.items()

        # Test DNE
        self.helper_dne(items)

        # Test Items
        self.helper_ab_immutable(10, items)

class MutableMappingMixin(MutableMixin, MappingMixin):

    def test_setitem(self):

        def setitem(instance, key, val):
            instance[key] = val

        # Test DNE
        self.helper_dne(setitem, "key_a", "val_a")

        # Create Instance
        i_key = self.generate_key()
        i_val_1 = {"key_a": "val_a_1", "key_b": "val_b_1", "key_c": "val_c_1"}
        i_val_2 = {"key_a": "val_a_2", "key_b": "val_b_2", "key_c": "val_c_2"}
        i_val_3 = {"key_d": "val_d", "key_e": "val_e", "key_f": "val_f"}
        instance = self.factory.from_new(i_key, i_val_1)

        # Test Existing Keys
        for k, v in i_val_2.iteritems():
            self.helper_ab_mutable_core(instance, i_val_1, setitem, k, v)

        # Test New Keys
        for k, v in i_val_3.iteritems():
            self.helper_ab_mutable_core(instance, i_val_1, setitem, k, v)

        # Cleanup
        instance.rem()

    def test_delitem(self):

        def delitem(instance, key):
            del(instance[key])

        # Test DNE
        self.helper_dne(delitem, "key_a")

        # Create Instance
        i_key = self.generate_key()
        i_val = {"key_a": "val_a", "key_b": "val_b", "key_c": "val_c"}
        instance = self.factory.from_new(i_key, i_val)

        # Test Existing Keys
        for k in i_val.keys():
            self.helper_ab_mutable_core(instance, i_val, delitem, k)
        self.assertEqual(0, len(instance))
        self.assertEqual(0, len(i_val))

        # Test Bad Key
        self.helper_raises_core(instance, i_val, KeyError, delitem, "key_d")

        # Cleanup
        instance.rem()

    def test_pop(self):

        def pop(instance, key):
            return instance.pop(key)

        def pop_default(instance, key, default):
            return instance.pop(key, default)

        # Test DNE
        self.helper_dne(pop, "key_a")
        self.helper_dne(pop_default, "key_a", None)

        # Create Instance
        i_key = self.generate_key()
        i_val = {"key_a": "val_a", "key_b": "val_b", "key_c": "val_c"}
        instance = self.factory.from_new(i_key, i_val)

        # Test Bad Key (Full)
        self.helper_raises_core(instance, i_val, KeyError, pop, "key_d")
        self.helper_ab_mutable_core(instance, i_val, pop_default, "key_d", "val_x")
        self.helper_exp_mutable_core(instance, i_val, "val_x", i_val, pop_default, "key_d", "val_x")

        # Test Key w/ Default
        self.helper_ab_mutable_core(instance, i_val, pop_default, "key_a", "val_x")

        # Test Remaining Keys
        for k in i_val.keys():
            self.helper_ab_mutable_core(instance, i_val, pop, k)
        self.assertEqual(0, len(instance))
        self.assertEqual(0, len(i_val))

        # Test Bad Key (Empty)
        self.helper_raises_core(instance, i_val, KeyError, pop, "key_a")
        self.helper_ab_mutable_core(instance, i_val, pop_default, "key_a", "val_X")
        self.helper_exp_mutable_core(instance, i_val, "val_x", {}, pop_default, "key_d", "val_x")

        # Cleanup
        instance.rem()

    def test_popitem(self):

        def popitem(instance):
            return instance.popitem()

        # Test DNE
        self.helper_dne(popitem)

        # Create Instance
        i_key = self.generate_key()
        i_val = {"key_a": "val_a", "key_b": "val_b", "key_c": "val_c"}
        instance = self.factory.from_new(i_key, i_val)

        # Test Existing Keys
        while len(instance) > 0:
            k, v = popitem(instance)
            self.assertIn(k, i_val)
            self.assertNotIn(k, instance)
            self.assertEqual(i_val[k], v)
            del(i_val[k])
        self.assertEqual(0, len(instance))
        self.assertEqual(0, len(i_val))
        self.assertEqual(instance.get_val(), i_val)

        # Test Empty
        self.helper_raises_core(instance, i_val, KeyError, popitem)

        # Cleanup
        instance.rem()

    def test_clear(self):

        def clear(instance):
            instance.clear()

        # Test DNE
        self.helper_dne(clear)

        # Create Instance
        i_key = self.generate_key()
        i_val = {"key_a": "val_a", "key_b": "val_b", "key_c": "val_c"}
        self.assertGreater(len(i_val), 0)
        instance = self.factory.from_new(i_key, i_val)
        self.assertGreater(len(instance), 0)
        self.assertEqual(instance.get_val(), i_val)

        # Test Full
        clear(instance)
        self.assertEqual(0, len(instance))
        clear(i_val)
        self.assertEqual(0, len(i_val))
        self.assertEqual(instance.get_val(), i_val)

        # Test Empty
        clear(instance)
        self.assertEqual(0, len(instance))
        clear(i_val)
        self.assertEqual(0, len(i_val))
        self.assertEqual(instance.get_val(), i_val)

        # Cleanup
        instance.rem()

    def test_update(self):

        def update(instance, d):
            instance.update(d)

        # Test DNE
        self.helper_dne(update, {"key_a": "val_a"})

        # Create Instance
        i_key = self.generate_key()
        i_val = {}
        i_val_1 = {"key_a": "val_a_1", "key_b": "val_b_1", "key_c": "val_c_1"}
        i_val_2 = {"key_b": "val_b_2", "key_c": "val_c_2", "key_d": "val_d_2"}
        instance = self.factory.from_new(i_key, i_val)
        self.assertEqual(instance.get_val(), i_val)

        # Test Empty
        update(instance, i_val_1)
        update(i_val, i_val_1)
        self.assertEqual(instance.get_val(), i_val)

        # Test Overwrite
        update(instance, i_val_2)
        update(i_val, i_val_2)
        self.assertEqual(instance.get_val(), i_val)

        # Cleanup
        instance.rem()

    def test_setdefault(self):

        def setdefault(instance, k, d):
            return instance.setdefault(k, d)

        def setdefaultdefault(instance, k):
            return instance.setdefault(k)

        # Test DNE
        self.helper_dne(setdefault, "key_a", "val_def")
        self.helper_dne(setdefaultdefault, "key_a")

        # Create Instance
        i_key = self.generate_key()
        i_val = {}
        instance = self.factory.from_new(i_key, i_val)
        self.assertEqual(instance.get_val(), i_val)

        # Test Empty
        ret = setdefault(instance, "key_a", "val_a")
        ref = setdefault(i_val, "key_a", "val_a")
        self.assertEqual(ret, "val_a")
        self.assertEqual(ret, ref)
        self.assertEqual(instance.get_val(), i_val)

        # Test Overwrite
        ret = setdefault(instance, "key_a", "val_b")
        ref = setdefault(i_val, "key_a", "val_b")
        self.assertEqual(ret, "val_a")
        self.assertEqual(ret, ref)
        self.assertEqual(instance.get_val(), i_val)

        # Test Default
        # TODO: Add support for None-type
        self.assertRaises(TypeError, setdefaultdefault, instance, "key_b")
        # ret = setdefaultdefault(instance, "key_b")
        # ref = setdefaultdefault(i_val, "key_b")
        # self.assertEqual(ret, None)
        # self.assertEqual(ret, ref)
        # self.assertEqual(instance.get_val(), i_val)

        # Test Default Overwrite
        ret = setdefaultdefault(instance, "key_a")
        ref = setdefaultdefault(i_val, "key_a")
        self.assertEqual(ret, "val_a")
        self.assertEqual(ret, ref)
        self.assertEqual(instance.get_val(), i_val)

        # Cleanup
        instance.rem()


### Object Mixins ###

class StringMixin(SequenceMixin):

    def __init__(self, *args, **kwargs):
        super(StringMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.keyval.InstanceFactory(self.driver, self.module.String)

    def generate_val_single(self, exclude=None):

        if exclude is None:
            exclude = ""
        while True:
            cnt = self.val_cnt % 26
            val = chr(ord('A') + cnt)
            if val not in exclude:
                self.val_cnt += 1
                break
        return str(val)

    def generate_val_multi(self, size, exclude=None):

        val = ""
        while size:
            val += self.generate_val_single(exclude=exclude)
            size -= 1
        return str(val)

    def generate_vals_sorted(self, size, cnt):

        vals = []
        while cnt:
            val = self.generate_val_multi(size)
            vals.append(val)
            cnt -= 1
        return sorted(vals)

class MutableStringMixin(MutableSequenceMixin, StringMixin):

    class MutableStringRef(collections.MutableSequence, object):

        def __init__(self, val):

            # Call Parent
            super(MutableStringMixin.MutableStringRef, self).__init__()

            # Save Val
            self._val = val

        def __unicode__(self):
            """Return Unicode Representation"""
            return unicode(self._val)

        def __str__(self):
            """Return String Representation"""
            return unicode(self).encode(keyval.keyval._ENCODING)

        def __repr__(self):
            """Return Unique Representation"""
            return repr(self._val)

        def __nonzero__(self):
            """Test Bool"""
            return bool(self._val)

        def __eq__(self, other):
            """Test Equality"""
            return self._val == other

        def __ne__(self, other):
            """Test Unequality"""
            return self._val != other

        def __lt__(self, other):
            """Test Less Than"""
            return self._val < other

        def __le__(self, other):
            """Test Less Than or Equal"""
            return self._val <= other

        def __gt__(self, other):
            """Test Greater Than"""
            return self._val > other

        def __ge__(self, other):
            """Test Greater Than or Equal"""
            return self._val >= other

        def __len__(self):
            """Get Len of Set"""
            return len(self._val)

        def __getitem__(self, i):
            """Get Seq Item"""
            return self._val[i]

        def __setitem__(self, idx, item):
            """Set Seq Item"""

            val_in = self._val
            val_out = ""
            if (idx != 0) and (idx != -len(val_in)):
                val_out += val_in[:idx]
            val_out += item
            if (idx != (len(val_in)-1)) and (idx != -1):
                val_out += val_in[idx+1:]
            self._val = val_out

        def __delitem__(self, idx):
            """Del Seq Item"""

            val_in = self._val
            val_out = ""
            if (idx != 0) and (idx != -len(val_in)):
                val_out += val_in[:idx]
            if (idx != (len(val_in)-1)) and (idx != -1):
                val_out += val_in[idx+1:]
            self._val = val_out

        def insert(self, idx, item):
            """Insert Seq Item"""
            val_in = self._val
            self._val = val_in[:idx] + item + val_in[idx:]

    def __init__(self, *args, **kwargs):
        super(MutableStringMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.keyval.InstanceFactory(self.driver, self.module.MutableString)

    def generate_val_single(self, exclude=None):

        if exclude is None:
            exclude = ""
        while True:
            cnt = self.val_cnt % 26
            val = chr(ord('A') + cnt)
            if val not in exclude:
                self.val_cnt += 1
                break
        return str(val)

    def generate_val_multi(self, size, exclude=None):

        val = ""
        while size:
            val += self.generate_val_single(exclude=exclude)
            size -= 1
        return self.MutableStringRef(val)

    def generate_vals_sorted(self, size, cnt):

        vals = []
        while cnt:
            val = self.generate_val_multi(size)
            vals.append(val)
            cnt -= 1
        return sorted(vals)

class ListMixin(SequenceMixin):

    def __init__(self, *args, **kwargs):
        super(ListMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.keyval.InstanceFactory(self.driver, self.module.List)

    def generate_val_single(self, exclude=None):

        if exclude is None:
            exclude = []
        while True:
            val = self.val_cnt
            if val not in exclude:
                self.val_cnt += 1
                break
        return str(val)

    def generate_val_multi(self, size, exclude=None):

        val = []
        while size:
            val.append(self.generate_val_single(exclude=exclude))
            size -= 1
        return list(val)

    def generate_vals_sorted(self, size, cnt):

        vals = []
        while cnt:
            val = self.generate_val_multi(size)
            vals.append(val)
            cnt -= 1
        return sorted(vals)

class MutableListMixin(MutableSequenceMixin, ListMixin):

    def __init__(self, *args, **kwargs):
        super(MutableListMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.keyval.InstanceFactory(self.driver, self.module.MutableList)

class SetMixin(BaseSetMixin):

    def __init__(self, *args, **kwargs):
        super(SetMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.keyval.InstanceFactory(self.driver, self.module.Set)

    def generate_val_single(self, exclude=None):

        if exclude is None:
            exclude = []
        while True:
            val = self.val_cnt
            if val not in exclude:
                self.val_cnt += 1
                break
        return str(val)

    def generate_val_multi(self, size, exclude=None):

        val = []
        while size:
            val.append(self.generate_val_single(exclude=exclude))
            size -= 1
        return set(val)

    def generate_vals_sorted(self, size, cnt):

        del(size)
        vals = []
        base = []
        while cnt:
            base.append(self.generate_val_single())
            vals.append(set(base))
            cnt -= 1
        return vals

class MutableSetMixin(MutableBaseSetMixin, SetMixin):

    def __init__(self, *args, **kwargs):
        super(MutableSetMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.keyval.InstanceFactory(self.driver, self.module.MutableSet)

class DictionaryMixin(MappingMixin):

    def __init__(self, *args, **kwargs):
        super(DictionaryMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.keyval.InstanceFactory(self.driver, self.module.Dictionary)

    def generate_val_single(self, exclude=None):

        TEST_MAP_KEY_PRE_STRING = "TESTMAPKEY"
        TEST_MAP_VAL_PRE_STRING = "TESTMAPVAL"

        if exclude is None:
            exclude = []
        while True:
            map_key = TEST_MAP_KEY_PRE_STRING + str(self.val_cnt)
            map_val = TEST_MAP_VAL_PRE_STRING + str(self.val_cnt)
            if map_key not in exclude:
                self.val_cnt += 1
                break
        return (map_key, map_val)

    def generate_val_multi(self, size, exclude=None):

        multi = {}
        while size:
            map_key, map_val = self.generate_val_single(exclude=exclude)
            multi[map_key] = map_val
            size -= 1
        return dict(multi)

    def generate_vals_sorted(self, size, cnt):

        vals = []
        while cnt:
            val = self.generate_val_multi(size)
            vals.append(val)
            cnt -= 1
        return sorted(vals)

class MutableDictionaryMixin(MutableMappingMixin, DictionaryMixin):

    def __init__(self, *args, **kwargs):
        super(MutableDictionaryMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.keyval.InstanceFactory(self.driver, self.module.MutableDictionary)
