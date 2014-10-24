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

    def test_from_new_good(self):

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


### Object Classes ###

class StringMixin(PersistentObjectMixin):

    def __init__(self, *args, **kwargs):
        super(StringMixin, self).__init__(*args, **kwargs)
        self.factory = keyval.base.InstanceFactory(self.driver, self.module.String)

    def generate_val(self):
        val = "{:s}_{:d}".format(_TEST_VAL_PRE_STRING, self.val_cnt)
        self.val_cnt += 1
        return val
