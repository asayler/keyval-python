# -*- coding: utf-8 -*-


# Andy Sayler
# Summer 2014
# Univerity of Colorado


### Imports ###

## stdlib ##
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


### Intermediate Classes ###

class PersistentObjectMixin(object):

    def __init__(self, *args, **kwargs):
        super(PersistentObjectMixin, self).__init__(*args, **kwargs)

    def test_from_new(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertEqual(val, instance.val())

        # Cleanup
        instance.rem()

    def test_from_existing(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

        # Create New Instance
        self.factory.from_new(key, val)

        # Get Existing Instance
        instance = self.factory.from_existing(key)
        self.assertTrue(instance)
        self.assertTrue(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertEqual(val, instance.val())

        # Cleanup
        instance.rem()

    def test_from_raw(self):

        # Setup Test Vals
        key = self.generate_key()
        val = None

        # Get Raw Instance
        instance = self.factory.from_raw(key)
        self.assertFalse(instance)
        self.assertFalse(instance.exists())
        self.assertEqual(key, instance.key())
        self.assertEqual(val, instance.val())

        # Cleanup
        instance.rem()

    def test_unicode(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(unicode(val), unicode(instance))

        # Cleanup
        instance.rem()

    def test_string(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(str(val), str(instance))

        # Cleanup
        instance.rem()

    def test_repr(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(key, repr(instance))

        # Cleanup
        instance.rem()

    def test_hash(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertEqual(hash(key), hash(instance))

        # Cleanup
        instance.rem()

    def test_bool(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

        # Create New Instance
        instance = self.factory.from_new(key, val)
        self.assertTrue(instance)

        # Cleanup
        instance.rem()

    def test_eq(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

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
        val = self.generate_val()
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


### Object Classes ###

class SequenceMixin(PersistentObjectMixin):

    def __init__(self, *args, **kwargs):
        super(SequenceMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.base.InstanceFactory(self.driver, self.module.String)

    def generate_val(self):
        val = "{:s}_{:d}".format(_TEST_VAL_PRE_STRING, self.val_cnt)
        self.val_cnt += 1
        return val

    def test_len(self):

        # Setup Test Vals
        key = self.generate_key()
        val = self.generate_val()

        # Create Instance
        instance = self.factory.from_raw(key)
        self.assertEqual(0, len(instance))
        instance = self.factory.from_new(key, val)
        self.assertEqual(len(val), len(instance))

        # Cleanup
        instance.rem()
