# -*- coding: utf-8 -*-


# Andy Sayler
# Summer 2014
# Univerity of Colorado


### Imports ###

## stdlib ##
import copy
import unittest
import warnings

### keyval ###
import keyval.base


### Globals ###

_TEST_KEY_PRE = "TESTKEY"
_TEST_VAL_PRE_STRING = "TESTVAL"

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
        self.assertEqual(val, instance.get_val())
        self.assertRaises(error, test_func, instance, *args)
        instance.rem()

    def helper_dne(self, test_func, *args):

        key = self.generate_key()
        instance = self.factory.from_raw(key)
        self.assertFalse(instance.exists())
        self.assertRaises(keyval.base.ObjectDNE, test_func, instance, *args)

    def helper_cmp_immutable(self, size, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())
        self.assertEqual(val, instance.get_val())
        orig_val = copy.copy(val)
        ret = test_func(instance, *args)
        ref = test_func(val, *args)
        self.assertEqual(ret, ref)
        self.assertEqual(orig_val, instance.get_val())
        self.assertEqual(orig_val, val)
        instance.rem()

    def test_from_new(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create Invalid Instance
        self.assertRaises(ValueError, self.factory.from_new, None, None)
        self.assertRaises(ValueError, self.factory.from_new, key, None)
        self.assertRaises(ValueError, self.factory.from_new, None, val)

        # Create Valid Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertEqual(val, instance.get_val())

        # Recreate Instance
        self.assertRaises(keyval.base.ObjectExists, self.factory.from_new, key, val)

        # Cleanup
        instance.rem()

    def test_from_existing(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Get Invalid Instance
        self.assertRaises(ValueError, self.factory.from_existing, None)

        # Get Nonexistant Instance
        self.assertRaises(keyval.base.ObjectDNE, self.factory.from_existing, key)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance.exists())

        # Get Existing Instance
        instance = self.factory.from_existing(key)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertEqual(val, instance.get_val())

        # Cleanup
        instance.rem()

    def test_from_raw(self):

        # Setup Test Vals
        key = self.generate_key()

        # Get Invalid Instance
        self.assertRaises(ValueError, self.factory.from_raw, None)

        # Get Raw Instance
        instance = self.factory.from_raw(key)
        self.assertFalse(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertRaises(keyval.base.ObjectDNE, instance.get_val)

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
        self.assertRaises(keyval.base.ObjectDNE, instance.rem)

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
        self.assertRaises(keyval.base.ObjectDNE, instance.get_val)

    def test_key(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(key, instance.key())

        # Rem Instance
        instance.rem()
        self.assertEqual(key, instance.key())

    def test_unicode(self):

        # Test DNE
        self.helper_dne(unicode)

        # Test Good
        self.helper_cmp_immutable(10, unicode)

    def test_string(self):

        # Test DNE
        self.helper_dne(str)

        # Test Good
        self.helper_cmp_immutable(10, str)

    def test_bool(self):

        # Test DNE
        self.helper_dne(bool)

        # Test Good
        self.helper_cmp_immutable( 1, bool)
        self.helper_cmp_immutable(10, bool)

    def test_repr(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(key, repr(instance))

        # Cleanup
        instance.rem()

    def test_hash(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(hash(key), hash(instance))

        # Cleanup
        instance.rem()

    def test_eq(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create Instance
        instance_a = self.factory.from_new(key, val)
        instance_b = self.factory.from_existing(key)
        self.assertEqual(instance_a, instance_b)
        self.assertEqual(instance_b, instance_a)

        # Cleanup
        instance_b.rem()

    def test_ne(self):

        # Setup Test Vals
        key_a = self.generate_key()
        key_b = self.generate_key()
        val = self.generate_val_multi(10)
        self.assertNotEqual(key_a, key_b)

        # Create Instance
        instance_a = self.factory.from_new(key_a, val)
        instance_b = self.factory.from_new(key_b, val)
        self.assertNotEqual(val, instance_a)
        self.assertNotEqual(instance_a, val)
        self.assertNotEqual(val, instance_b)
        self.assertNotEqual(instance_b, val)
        self.assertNotEqual(instance_a, instance_b)

        # Cleanup
        instance_a.rem()
        instance_b.rem()

class MutableMixin(PersistentMixin):

    def helper_cmp_mutable(self, size, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.assertEqual(val, instance.get_val())
        ret = test_func(instance, *args)
        ref = test_func(val, *args)
        self.assertEqual(ret, ref)
        self.assertEqual(val, instance.get_val())
        instance.rem()

    def helper_exp_mutable(self, size, exp_ret, exp_val, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.assertEqual(val, instance.get_val())
        ret = test_func(instance, *args)
        self.assertEqual(exp_ret, ret)
        self.assertEqual(exp_val, instance.get_val())
        instance.rem()

    def test_set_val(self):

        def test_func(instance, new_val):
            instance.set_val(new_val)

        # Setup
        new_val = self.generate_val_multi(10)

        # Test DNE
        self.helper_dne(test_func, new_val)

        # Test Good
        self.helper_exp_mutable(10, None, new_val, test_func, new_val)

        # Test Bad
        self.helper_raises(10, ValueError, test_func, None)

class SequenceMixin(PersistentMixin):

    def test_len(self):

        # Test DNE
        self.helper_dne(len)

        # Test Good
        self.helper_cmp_immutable( 1, len)
        self.helper_cmp_immutable(10, len)

    def test_getitem(self):

        def getitem(instance, index):
            return instance[index]

        # Test DNE
        self.helper_dne(getitem, None)

        # Test Good
        for i in range(10):
            self.helper_cmp_immutable(10, getitem,  i    )
            self.helper_cmp_immutable(10, getitem, (i-10))

        # Test OOB
        self.helper_raises( 1, IndexError, getitem,   1)
        self.helper_raises( 1, IndexError, getitem,  -2)
        self.helper_raises(10, IndexError, getitem,  10)
        self.helper_raises(10, IndexError, getitem,  11)
        self.helper_raises(10, IndexError, getitem, -11)
        self.helper_raises(10, IndexError, getitem, -12)

    def test_contains(self):

        def contains(instance, item):
            return item in instance

        # Test DNE
        self.helper_dne(contains, None)

        # Test In
        def contains_in(instance, index):
            item = instance[index]
            return contains(instance, item)
        for i in range(10):
            self.helper_cmp_immutable(10, contains_in,  i    )
            self.helper_cmp_immutable(10, contains_in, (i-10))

        # Test Out
        def contains_out(instance):
            item = self.generate_val_single(exclude=instance)
            return contains(instance, item)
        self.helper_cmp_immutable(10, contains_out)

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
            self.helper_cmp_immutable(10, index_in,  i    )
            self.helper_cmp_immutable(10, index_in, (i-10))

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
            self.helper_cmp_immutable(10, count_in,  i)
            self.helper_cmp_immutable(10, count_in, (i-10))

        # Test Out
        def count_out(instance):
            item = self.generate_val_single(exclude=instance)
            return count(instance, item)
        self.helper_cmp_immutable(10, count_out)

    def test_iter(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create Instance
        instance = self.factory.from_new(key, val)

        # Test Instance
        cnt = 0
        for i in instance:
            self.assertEqual(val[cnt], i)
            cnt += 1

        # Cleanup
        instance.rem()

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
            self.helper_cmp_mutable(10, setitem,  i,     item)
            item = self.generate_val_single()
            self.helper_cmp_mutable(10, setitem, (i-10), item)

        # Test OOB
        item = self.generate_val_single()
        self.helper_raises( 1, IndexError, setitem,   1, item)
        self.helper_raises( 1, IndexError, setitem,  -2, item)
        self.helper_raises(10, IndexError, setitem,  10, item)
        self.helper_raises(10, IndexError, setitem,  11, item)
        self.helper_raises(10, IndexError, setitem, -11, item)
        self.helper_raises(10, IndexError, setitem, -12, item)

    def test_delitem(self):

        def delitem(instance, idx, item):
            del(instance[idx])

        # Test DNE
        item = self.generate_val_single()
        self.helper_dne(delitem, None, item)

        # Test Good
        for i in range(10):
            item = self.generate_val_single()
            self.helper_cmp_mutable(10, delitem,  i,     item)
            item = self.generate_val_single()
            self.helper_cmp_mutable(10, delitem, (i-10), item)

        # Test OOB
        item = self.generate_val_single()
        self.helper_raises(10, IndexError, delitem,  10, item)
        self.helper_raises(10, IndexError, delitem,  11, item)
        self.helper_raises(10, IndexError, delitem, -11, item)
        self.helper_raises(10, IndexError, delitem, -12, item)

    def test_insert(self):

        def insert(instance, idx, item):
            return instance.insert(idx, item)

        # Test DNE
        item = self.generate_val_single()
        self.helper_dne(insert, None, item)

        # Test Inside
        for i in range(10):
            item = self.generate_val_single()
            self.helper_cmp_mutable(10, insert,  i,     item)
            item = self.generate_val_single()
            self.helper_cmp_mutable(10, insert, (i-10), item)

        # Test Before
        item = self.generate_val_single()
        self.helper_cmp_mutable(10, insert, -11, item)
        self.helper_cmp_mutable(10, insert, -12, item)

        # Test After
        item = self.generate_val_single()
        self.helper_cmp_mutable(10, insert, 10, item)
        self.helper_cmp_mutable(10, insert, 11, item)


### Object Mixins ###

class StringMixin(SequenceMixin):

    def __init__(self, *args, **kwargs):
        super(SequenceMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.base.InstanceFactory(self.driver, self.module.String)

    def generate_val_single(self, exclude=None):

        if exclude is None:
            exclude = ""
        while True:
            cnt = self.val_cnt % 26
            val = chr(ord('A') + cnt)
            if val not in exclude:
                self.val_cnt += 1
                break
        return val

    def generate_val_multi(self, size, exclude=None):

        val = ""
        for i in range(size):
            val += self.generate_val_single(exclude=exclude)
        return val

    def test_empty(self):

        # Test Len
        self.helper_cmp_immutable( 0, len)

        # Test Bool
        self.helper_cmp_immutable( 0, bool)

        # Test getitem
        def getitem(instance, index):
            return instance[index]
        self.helper_raises( 0, IndexError, getitem,  0)
        self.helper_raises( 0, IndexError, getitem,  1)
        self.helper_raises( 0, IndexError, getitem, -1)

class ListMixin(SequenceMixin):

    def __init__(self, *args, **kwargs):
        super(ListMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.base.InstanceFactory(self.driver, self.module.List)

    def generate_val_single(self, exclude=None):

        if exclude is None:
            exclude = []
        while True:
            cnt = self.val_cnt % 26
            val = chr(ord('A') + cnt)
            if val not in exclude:
                self.val_cnt += 1
                break
        return val

    def generate_val_multi(self, size, exclude=None):

        val = []
        for i in range(size):
            val.append(self.generate_val_single(exclude=exclude))
        return val

    def test_empty(self):

        # Create Empty Instance
        key = self.generate_key()
        val = self.generate_val_multi(0)
        self.assertRaises(ValueError, self.factory.from_new, key, val)

class MutableListMixin(MutableSequenceMixin, ListMixin):

    def __init__(self, *args, **kwargs):
        super(ListMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.base.InstanceFactory(self.driver, self.module.MutableList)
