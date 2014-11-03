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

    def generate_val_multi(self, size, exclude=None):

        val = self.generate_val_single(null=True)
        for i in range(size):
            val += self.generate_val_single(exclude=exclude)
        return val

### Base Mixins ###

class PersistentMixin(object):

    def __init__(self, *args, **kwargs):
        super(PersistentMixin, self).__init__(*args, **kwargs)

    def helper_raises_args(self, size, error, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.assertEqual(val, instance.get_val())
        self.assertRaises(error, test_func, instance, *args)
        instance.rem()

    def helper_dne_args(self, test_func, *args):

        key = self.generate_key()
        instance = self.factory.from_raw(key)
        self.assertFalse(instance.exists())
        self.assertRaises(keyval.base.ObjectDNE, test_func, instance, *args)

    def helper_test_args_immutable(self, size, test_func, *args):

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
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

        # No Cleanup

    def test_unicode(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(unicode(val), unicode(instance))

        # Cleanup
        instance.rem()

    def test_string(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(str(val), str(instance))

        # Cleanup
        instance.rem()

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

    def test_bool(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val_multi(10)

        # Test Non-existent Instance
        instance = self.factory.from_raw(key)
        self.assertFalse(instance)

        # Test New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance)

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

    def __init__(self, *args, **kwargs):
        super(MutableMixin, self).__init__(*args, **kwargs)

    def helper_test_args_mutable(self, size, test_func, ref_func=None, *args):

        if ref_func is None:
            ref_func = test_func

        key = self.generate_key()
        val = self.generate_val_multi(size)
        instance = self.factory.from_new(key, val)
        self.assertEqual(val, instance.get_val())
        ret = test_func(instance, *args)
        ref = ref_func(val, *args)
        self.assertEqual(ret, ref)
        self.assertEqual(val, instance.get_val())
        instance.rem()

    def test_set_val(self):

        def test_func(instance, new_val):
            instance.set_val(new_val)

        # Setup
        new_val = self.generate_val_multi(10)

        # Test DNE
        self.helper_dne_args(test_func, new_val)

        # Test Good
        self.helper_test_args_mutable(10, test_func, new_val)

        # Test Bad
        self.helper_raises_args(10, ValueError, test_func, None)

class SequenceMixin(PersistentMixin):

    def __init__(self, *args, **kwargs):
        super(SequenceMixin, self).__init__(*args, **kwargs)

        # Test DNE
        self.helper_dne_args(len)

        # Test Good
        for i in range(10):
            self.helper_test_args_immutable( 0, len)
            self.helper_test_args_immutable(10, len)

    def test_getitem(self):

        def getitem(instance, index):
            return instance[index]

        # Test DNE
        self.helper_dne_args(getitem, None)

        # Test Good
        for i in range(10):
            self.helper_test_args_immutable(10, getitem,  i,   )
            self.helper_test_args_immutable(10, getitem, (i-10))

        # Test OOB
        self.helper_raises_args( 0, IndexError, getitem,   0)
        self.helper_raises_args( 0, IndexError, getitem,   1)
        self.helper_raises_args( 0, IndexError, getitem,  -1)
        self.helper_raises_args(10, IndexError, getitem,  10)
        self.helper_raises_args(10, IndexError, getitem,  11)
        self.helper_raises_args(10, IndexError, getitem, -11)
        self.helper_raises_args(10, IndexError, getitem, -12)

    def test_contains(self):

        def contains(instance, item):
            return item in instance

        # Test DNE
        self.helper_dne_args(contains, None)

        # Test In
        def contains_in(instance, index):
            item = instance[index]
            return contains(instance, item)
        for i in range(10):
            self.helper_test_args_immutable(10, contains_in,  i,   )
            self.helper_test_args_immutable(10, contains_in, (i-10))

        # Test Out
        def contains_out(instance):
            item = self.generate_val_single(exclude=instance)
            return contains(instance, item)
        self.helper_test_args_immutable(10, contains_out)

    def test_index(self):

        def index(instance, item):
            return instance.index(item)

        # Test DNE
        self.helper_dne_args(index, None)

        # Test In
        def index_in(instance, idx):
            item = instance[idx]
            return index(instance, item)
        for i in range(10):
            self.helper_test_args_immutable(10, index_in,  i    )
            self.helper_test_args_immutable(10, index_in, (i-10))

        # Test Out
        def index_out(instance):
            item = self.generate_val_single(exclude=instance)
            return index(instance, item)
        self.helper_raises_args(10, ValueError, index_out)

    def test_count(self):

        def count(instance, item):
            return instance.count(item)

        # Test DNE
        self.helper_dne_args(count, None)

        # Test In
        def count_in(instance, index):
            item = instance[index]
            return count(instance, item)
        for i in range(10):
            self.helper_test_args_immutable(10, count_in,  i)
            self.helper_test_args_immutable(10, count_in, (i-10))

        # Test Out
        def count_out(instance):
            item = self.generate_val_single(exclude=instance)
            return count(instance, item)
        self.helper_test_args_immutable(10, count_out)

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

    def __init__(self, *args, **kwargs):
        super(MutableSequenceMixin, self).__init__(*args, **kwargs)

    def helper_test_index_item(self, test_func, index, item, size, ref_func):

        key = self.generate_key()
        old = self.generate_val_multi(size)
        instance = self.factory.from_new(key, old)
        self.assertEqual(old, instance.get_val())
        ret = test_func(instance, index, item)
        new = ref_func(old, index, item)
        self.assertNotEqual(old, new)
        self.assertEqual(new, instance.get_val())
        instance.rem()
        return ret

    def test_setitem(self):

        # Test Functions

        def test_func(instance, index, item):
            ret = instance[index] = item
            return ret

        def ref_func(ref, index, item):
            out = self.generate_val_multi(0)
            if (index != 0) and (index != -len(ref)):
                out += ref[:index]
            out += item
            if (index != (len(ref)-1)) and (index != -1):
                out += ref[index+1:]
            return out

        # Test Wrappers

        def setitem_test_good(index, size):
            item = self.generate_val_multi(1)
            ret = self.helper_test_index_item(test_func, index, item, size, ref_func)
            self.assertEqual(item, ret)

        def setitem_test_null(index):
            item = self.generate_val_multi(1)
            self.helper_dne_args(test_func, index, item)

        def setitem_test_badval(index, size):
            item = self.generate_val_multi(3)
            self.helper_raises_args(size, ValueError, test_func, index, item)

        def setitem_test_oob(index, size):
            item = self.generate_val_multi(1)
            self.helper_raises_args(size, IndexError, test_func, index, item)

        # Test Values

        # Test Null Instance
        setitem_test_null( 0)
        setitem_test_null(-1)
        setitem_test_null( 1)

        # Test Empty Instance
        setitem_test_oob( 0, 0)
        setitem_test_oob( 1, 0)
        setitem_test_oob(-1, 0)

        # Test Valid
        setitem_test_good(  0, 10)
        setitem_test_good(-10, 10)
        setitem_test_good(  5, 10)
        setitem_test_good( -5, 10)
        setitem_test_good(  9, 10)
        setitem_test_good( -1, 10)

        # Test OOB
        setitem_test_oob( 10, 10)
        setitem_test_oob( 11, 10)
        setitem_test_oob(-11, 10)
        setitem_test_oob(-12, 10)

        # Test Bad Val
        setitem_test_badval(  0, 10)
        setitem_test_badval(-10, 10)
        setitem_test_badval(  5, 10)
        setitem_test_badval( -5, 10)
        setitem_test_badval(  9, 10)
        setitem_test_badval( -1, 10)

    def test_delitem(self):

        def test_func(instance, index, item):
            del(instance[index])

        def ref_func(ref, index, item):
            out = self.generate_val_multi(0)
            if (index != 0) and (index != -len(ref)):
                out += ref[:index]
            if (index != (len(ref)-1)) and (index != -1):
                out += ref[index+1:]
            return out

        def delitem_test_good(index, size):
            item = self.generate_val_multi(1)
            ret = self.helper_test_index_item(test_func, index, item, size, ref_func)
            self.assertIsNone(ret)

        def delitem_test_null(index):
            item = self.generate_val_multi(1)
            self.helper_dne_args(test_func, index, item)

        def delitem_test_oob(index, size):
            item = self.generate_val_multi(1)
            self.helper_raises_args(size, IndexError, test_func, index, item)

        # Test Null Instance
        delitem_test_null( 0)
        delitem_test_null(-1)
        delitem_test_null( 1)

        # Test Empty Instance
        delitem_test_oob( 0, 0)
        delitem_test_oob( 1, 0)
        delitem_test_oob(-1, 0)

        # Test Valid
        delitem_test_good(  0, 10)
        delitem_test_good(-10, 10)
        delitem_test_good(  5, 10)
        delitem_test_good( -5, 10)
        delitem_test_good(  9, 10)
        delitem_test_good( -1, 10)

        # Test OOB
        delitem_test_oob( 10, 10)
        delitem_test_oob( 11, 10)
        delitem_test_oob(-11, 10)
        delitem_test_oob(-12, 10)

    def test_insert(self):

        def test_func(instance, index, item):
            return instance.insert(index, item)

        def ref_func(ref, index, item):
            return ref[:index] + item + ref[index:]

        def insert_test_good(index, size):
            item = self.generate_val_multi(1)
            ret = self.helper_test_index_item(test_func, index, item, size, ref_func)
            self.assertIsNone(ret)

        def insert_test_badval(index, size):
            item = self.generate_val_multi(3)
            self.helper_raises_args(size, ValueError, test_func, index, item)

        def insert_test_null(index):
            item = self.generate_val_multi(1)
            self.helper_dne_args(test_func, index, item)

        # test Null Instance
        insert_test_null( 0)
        insert_test_null( 1)
        insert_test_null(-1)

        # Test Bad Val
        insert_test_badval(  0, 10)
        insert_test_badval(-10, 10)
        insert_test_badval(  5, 10)
        insert_test_badval( -5, 10)
        insert_test_badval(  9, 10)
        insert_test_badval( -1, 10)

        # Test Empty Instance
        insert_test_good( 0, 0)
        insert_test_good( 1, 0)
        insert_test_good(-1, 0)

        # Test Insert Before
        insert_test_good(-12, 10)
        insert_test_good(-11, 10)

        # Test Insert Beginning
        insert_test_good(  0, 10)
        insert_test_good(-10, 10)

        # Test Instance - Middle
        insert_test_good( 5, 10)
        insert_test_good(-5, 10)

        # Test Insert End
        insert_test_good( 9, 10)
        insert_test_good(-1, 10)

        # Test Instert After
        insert_test_good(10, 10)
        insert_test_good(11, 10)


### Object Mixins ###

class StringMixin(SequenceMixin):

    def __init__(self, *args, **kwargs):
        super(SequenceMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.base.InstanceFactory(self.driver, self.module.String)

    def generate_val_single(self, exclude=None, null=False):

        if not null:
            if exclude is None:
                exclude = ""
            while True:
                cnt = self.val_cnt % 26
                val = chr(ord('A') + cnt)
                if val not in exclude:
                    self.val_cnt += 1
                    break
        else:
            val = ""

        return val
