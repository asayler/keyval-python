#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado

import copy
import random
import time
import unittest
import uuid
import os

import redis

import keyval.backend_redis as backend


DUMMY_SCHEMA   = ['key1', 'key2', 'key3']
DUMMY_TESTDICT = {'key1': "val1",
                  'key2': "val2",
                  'key3': "val3"}

db = redis.StrictRedis(db=9)


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.db = db
        if (self.db.dbsize() != 0):
            raise CogsTestError("Test Database Not Empty: {}".format(self.db.dbsize()))

    def tearDown(self):
        self.db.flushdb()

    def assertSubset(self, sub, sup):

        if type(sub) != type(sup):
            raise CogsTestError("sub, sup must be of same type")

        if type(sub) == dict:
            for k in sub:
                self.assertEqual(str(sub[k]), str(sup[k]))
        elif type(sub) == set:
            self.assertTrue(sub.issubset(sup))
        elif type(sub) == list:
            self.assertTrue(set(sub).issubset(set(sup)))
        else:
            raise CogsTestError("Unhandled type: {:s}".format(type(sub)))

class BackendRedisTestCase(BaseTestCase):

    def setUp(self):
        super(BackendRedisTestCase, self).setUp()

    def tearDown(self):
        super(BackendRedisTestCase, self).tearDown()


class RedisObjectTestCase(BackendRedisTestCase):

    def setUp(self):
        super(RedisObjectTestCase, self).setUp()

        self.key = 'key'
        self.cls_name = backend.TypedObject.__name__.lower()
        self.rid = "{:s}+{:s}".format(self.cls_name, self.key).lower()
        self.val = 'val'

        self.db.set(self.rid, self.val)

        self.ObjFactory = backend.PrefixedFactory(backend.TypedObject)

    def tearDown(self):
        super(RedisObjectTestCase, self).tearDown()

    def test_from_new(self):

        # Test w/o Key
        obj = self.ObjFactory.from_new()
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}".format(self.cls_name))

        # Test w/ Key
        key = 'newkey'
        obj = self.ObjFactory.from_new(key=key)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}+{:s}".format(self.cls_name, key))

        # Test w/ Duplicate Key
        self.assertRaises(backend.PersistentObjectError, self.ObjFactory.from_new, key=self.key)

        # Test w/ Illegal Key ':'
        self.assertRaises(backend.PersistentObjectError, self.ObjFactory.from_new, key='test:1')

        # Test w/ Illegal Key '+'
        self.assertRaises(backend.PersistentObjectError, self.ObjFactory.from_new, key='test+1')

    def test_from_existing(self):

        # Test Non-Existant Object
        self.assertRaises(backend.ObjectDNE, self.ObjFactory.from_existing, key='badkey')

        # Test Existing Object
        self.assertTrue(self.ObjFactory.from_existing(key=self.key))

    def test_from_raw(self):

        # Test Non-Existant Object
        self.assertTrue(self.ObjFactory.from_existing(key=self.key))

        # Test Existing Object
        self.assertTrue(self.ObjFactory.from_existing(key=self.key))

    def test_str(self):

        # Test Not Equal
        s1 = str(self.ObjFactory.from_new(key='str1'))
        s2 = str(self.ObjFactory.from_new(key='str2'))
        self.assertFalse(s1 == s2)

        # Test Equal
        s1 = str(self.ObjFactory.from_new(key='str1'))
        s2 = str(self.ObjFactory.from_new(key='str1'))
        self.assertTrue(s1 == s2)

    def test_hash(self):

        # Test Not Equal
        h1 = hash(self.ObjFactory.from_new(key='hash1'))
        h2 = hash(self.ObjFactory.from_new(key='hash2'))
        self.assertFalse(h1 == h2)

        # Test Equal
        h1 = hash(self.ObjFactory.from_new(key='hash1'))
        h2 = hash(self.ObjFactory.from_new(key='hash1'))
        self.assertTrue(h1 == h2)

    def test_eq(self):

        # Test Not Equal
        o1 = self.ObjFactory.from_new(key='eq1')
        o2 = self.ObjFactory.from_new(key='eq2')
        self.assertFalse(o1 == o2)

        # Test Equal
        o1 = self.ObjFactory.from_new(key='eq1')
        o2 = self.ObjFactory.from_new(key='eq1')
        self.assertTrue(o1 == o2)

    def test_delete(self):

        # Test Delete
        o = self.ObjFactory.from_existing(key=self.key)
        self.assertTrue(self.db.exists(self.rid))
        o.delete()
        self.assertFalse(self.db.exists(self.rid))


class RedisFactoryTestCase(BackendRedisTestCase):

    def setUp(self):
        super(RedisFactoryTestCase, self).setUp()

    def tearDown(self):
        super(RedisFactoryTestCase, self).tearDown()

    def test_init(self):

        # Test w/o Prefix or Key
        of = backend.PrefixedFactory(backend.TypedObject)
        obj = of.from_new()
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}".format(of.cls.__name__).lower())

        # Test w/ Prefix but w/o Key
        pre = "testprefix"
        of = backend.PrefixedFactory(backend.TypedObject, prefix=pre)
        obj = of.from_new()
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}:{:s}".format(pre, of.cls.__name__).lower())

        # Test w/ Key but w/o Prefix
        key = "testkey"
        of = backend.PrefixedFactory(backend.TypedObject)
        obj = of.from_new(key=key)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}+{:s}".format(of.cls.__name__, key).lower())

        # Test w/ Prefix and Key
        pre = "testprefix"
        kwy = "testkey"
        of = backend.PrefixedFactory(backend.TypedObject, prefix=pre)
        obj = of.from_new(key=key)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}:{:s}+{:s}".format(pre, of.cls.__name__, key).lower())

    def test_list(self):

        val = 'val'
        pre = 'test'
        cls = backend.TypedObject.__name__.lower()

        # Add Parents w/o Prefix
        self.db.flushdb()
        parents = ['p01', 'p02', 'p03']
        for p in parents:
            self.db.set("{:s}+{:s}".format(cls, p).lower(), val)

        # Test Parents w/o Prefix
        hf = backend.PrefixedFactory(backend.TypedObject)
        fam = hf.list_family()
        self.assertEqual(set(parents), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(parents), sib)
        chd = hf.list_children()
        self.assertFalse(chd)

        # Add Parents w/ Prefix
        self.db.flushdb()
        parents = ['p01', 'p02', 'p03']
        for p in parents:
            self.db.set("{:s}:{:s}+{:s}".format(pre, cls, p), val)

        # Test Parents w/ Prefix
        hf = backend.PrefixedFactory(backend.TypedObject, prefix=pre)
        fam = hf.list_family()
        self.assertEqual(set(parents), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(parents), sib)
        chd = hf.list_children()
        self.assertEqual(set([]), chd)

        # Add Parents + Children w/o Prefix
        self.db.flushdb()
        parents = ['p01', 'p02', 'p03']
        for p in parents:
            self.db.set("{:s}+{:s}".format(cls, p), val)
        p1_children = ['c01', 'c02', 'c03']
        full_children = []
        for c in p1_children:
            child = "{:s}:{:s}+{:s}".format(parents[0], cls, c)
            self.db.set("{:s}+{:s}".format(cls, child), val)
            full_children.append(child)

        # Test Parents + Children w/o Prefix
        hf = backend.PrefixedFactory(backend.TypedObject)
        fam = hf.list_family()
        self.assertEqual(set(parents + full_children), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(parents), sib)
        chd = hf.list_children()
        self.assertEqual(set(full_children), chd)

        # Test Children w/o Prefix
        chd_pre = "{:s}+{:s}".format(cls, parents[0])
        hf = backend.PrefixedFactory(backend.TypedObject, prefix=chd_pre)
        fam = hf.list_family()
        self.assertEqual(set(p1_children), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(p1_children), sib)
        chd = hf.list_children()
        self.assertEqual(set([]), chd)

        # Add Parents + Children w/ Prefix
        self.db.flushdb()
        parents = ['p01', 'p02', 'p03']
        for p in parents:
            self.db.set("{:s}:{:s}+{:s}".format(pre, cls, p), val)
        p1_children = ['c01', 'c02', 'c03']
        full_children = []
        for c in p1_children:
            child = "{:s}:{:s}+{:s}".format(parents[0], cls, c)
            self.db.set("{:s}:{:s}+{:s}".format(pre, cls, child), val)
            full_children.append(child)

        # Test Parents + Children w/ Prefix
        hf = backend.PrefixedFactory(backend.TypedObject, prefix=pre)
        fam = hf.list_family()
        self.assertEqual(set(parents + full_children), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(parents), sib)
        chd = hf.list_children()
        self.assertEqual(set(full_children), chd)

        # Test Children w/ Prefix
        chd_pre = "{:s}:{:s}+{:s}".format(pre, cls, parents[0])
        hf = backend.PrefixedFactory(backend.TypedObject, prefix=chd_pre)
        fam = hf.list_family()
        self.assertEqual(set(p1_children), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(p1_children), sib)
        chd = hf.list_children()
        self.assertEqual(set([]), chd)


class RedisUUIDFactoryTestCase(BackendRedisTestCase):

    def setUp(self):
        super(RedisUUIDFactoryTestCase, self).setUp()

    def tearDown(self):
        super(RedisUUIDFactoryTestCase, self).tearDown()

    def test_init(self):

        # Test w/o Prefix
        of = backend.UUIDFactory(backend.TypedObject)
        o = of.from_new()
        self.assertTrue(o)

        # Test w/ Prefix
        p = "testprefix_{:03d}".format(random.randint(0, 999))
        of = backend.UUIDFactory(backend.TypedObject, prefix=p)
        o = of.from_new()
        self.assertTrue(o)

    def test_list(self):

        val = 'val'
        pre = 'test'
        cls = backend.TypedObject.__name__.lower()

        # Add Parents w/o Prefix
        self.db.flushdb()
        parents = ['p01', 'p02', 'p03']
        for p in parents:
            self.db.set("{:s}+{:s}".format(cls, p).lower(), val)

        # Test Parents w/o Prefix
        hf = backend.UUIDFactory(backend.TypedObject)
        fam = hf.list_family()
        self.assertEqual(set(parents), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(parents), sib)
        chd = hf.list_children()
        self.assertFalse(chd)

        # Add Parents w/ Prefix
        self.db.flushdb()
        parents = ['p01', 'p02', 'p03']
        for p in parents:
            self.db.set("{:s}:{:s}+{:s}".format(pre, cls, p), val)

        # Test Parents w/ Prefix
        hf = backend.UUIDFactory(backend.TypedObject, prefix=pre)
        fam = hf.list_family()
        self.assertEqual(set(parents), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(parents), sib)
        chd = hf.list_children()
        self.assertEqual(set([]), chd)

        # Add Parents + Children w/o Prefix
        self.db.flushdb()
        parents = ['p01', 'p02', 'p03']
        for p in parents:
            self.db.set("{:s}+{:s}".format(cls, p), val)
        p1_children = ['c01', 'c02', 'c03']
        full_children = []
        for c in p1_children:
            child = "{:s}:{:s}+{:s}".format(parents[0], cls, c)
            self.db.set("{:s}+{:s}".format(cls, child), val)
            full_children.append(child)

        # Test Parents + Children w/o Prefix
        hf = backend.UUIDFactory(backend.TypedObject)
        fam = hf.list_family()
        self.assertEqual(set(parents + full_children), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(parents), sib)
        chd = hf.list_children()
        self.assertEqual(set(full_children), chd)

        # Test Children w/o Prefix
        chd_pre = "{:s}+{:s}".format(cls, parents[0])
        hf = backend.UUIDFactory(backend.TypedObject, prefix=chd_pre)
        fam = hf.list_family()
        self.assertEqual(set(p1_children), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(p1_children), sib)
        chd = hf.list_children()
        self.assertEqual(set([]), chd)

        # Add Parents + Children w/ Prefix
        self.db.flushdb()
        parents = ['p01', 'p02', 'p03']
        for p in parents:
            self.db.set("{:s}:{:s}+{:s}".format(pre, cls, p), val)
        p1_children = ['c01', 'c02', 'c03']
        full_children = []
        for c in p1_children:
            child = "{:s}:{:s}+{:s}".format(parents[0], cls, c)
            self.db.set("{:s}:{:s}+{:s}".format(pre, cls, child), val)
            full_children.append(child)

        # Test Parents + Children w/ Prefix
        hf = backend.UUIDFactory(backend.TypedObject, prefix=pre)
        fam = hf.list_family()
        self.assertEqual(set(parents + full_children), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(parents), sib)
        chd = hf.list_children()
        self.assertEqual(set(full_children), chd)

        # Test Children w/ Prefix
        chd_pre = "{:s}:{:s}+{:s}".format(pre, cls, parents[0])
        hf = backend.UUIDFactory(backend.TypedObject, prefix=chd_pre)
        fam = hf.list_family()
        self.assertEqual(set(p1_children), fam)
        sib = hf.list_siblings()
        self.assertEqual(set(p1_children), sib)
        chd = hf.list_children()
        self.assertEqual(set([]), chd)


class RedisHashTestCase(BackendRedisTestCase):

    def setUp(self):
        super(RedisHashTestCase, self).setUp()

        self.HashFactory = backend.PrefixedFactory(backend.Hash)

    def tearDown(self):
        super(RedisHashTestCase, self).tearDown()

    def test_from_new(self):

        # Create Key
        key = "testkey"

        # Test Empty Dict w/o Key
        data = {}
        self.assertRaises(ValueError, self.HashFactory.from_new, data)

        # Test Empty Dict w/ Key
        data = {}
        self.assertRaises(ValueError, self.HashFactory.from_new, data, key=key)

        # Test Non-Empty Dict w/o Key
        data = copy.deepcopy(DUMMY_TESTDICT)
        obj = self.HashFactory.from_new(data)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}".format(self.HashFactory.cls.__name__).lower())

        # Test Non-Empty Dict w/ Key
        data = copy.deepcopy(DUMMY_TESTDICT)
        obj = self.HashFactory.from_new(data, key=key)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}+{:s}".format(self.HashFactory.cls.__name__, key).lower())
        self.assertSubset(data, obj.get_dict())

    def test_from_existing(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Test Non-Existant Object
        self.assertRaises(backend.ObjectDNE, self.HashFactory.from_existing, key=k)

        # Test Existing Object
        d = copy.deepcopy(DUMMY_TESTDICT)
        h1 = self.HashFactory.from_new(d, key=k)
        self.assertSubset(d, h1.get_dict())
        h2 = self.HashFactory.from_existing(key=k)
        self.assertEqual(h1, h2)
        self.assertEqual(h1.get_dict(), h2.get_dict())

    def test_from_raw(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Test Non-Existant Object
        d = copy.deepcopy(DUMMY_TESTDICT)
        h1 = self.HashFactory.from_raw(key=k)
        self.assertFalse(h1.get_dict())
        h1.set_dict(d)
        self.assertSubset(d, h1.get_dict())

        # Test Existing Object
        h2 = self.HashFactory.from_raw(key=k)
        self.assertSubset(d, h2.get_dict())

        # Compare Objects
        self.assertEqual(h1, h2)
        self.assertEqual(h1.get_dict(), h2.get_dict())

    def test_get_dict(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create and Get Object
        d_in = copy.deepcopy(DUMMY_TESTDICT)
        obj = self.HashFactory.from_new(d_in, key=k)
        d_out = obj.get_dict()
        self.assertSubset(d_in, d_out)

    def test_set_dict(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create and Get Object
        d1_in = copy.deepcopy(DUMMY_TESTDICT)
        obj = self.HashFactory.from_new(d1_in, key=k)
        d1_out = obj.get_dict()
        self.assertSubset(d1_in, d1_out)

        # Update and Get Object
        d2_in = copy.deepcopy(DUMMY_TESTDICT)
        for k in d2_in:
            d2_in[k] = "set_dict_test_val_{:s}".format(k)
        self.assertNotEqual(d1_in, d2_in)
        obj.set_dict(d2_in)
        d2_out = obj.get_dict()
        self.assertSubset(d2_in, d2_out)

    def test_getitem(self):

        # Temp Get Funcation
        def get_item(d, key):
            return d[key]

        # Create Object Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create Object
        d = copy.deepcopy(DUMMY_TESTDICT)
        obj = self.HashFactory.from_new(d, key=k)

        # Test Bad Key
        self.assertFalse(obj['test'])

        # Test Good Keys
        for key in d:
            self.assertEqual(d[key], obj[key])

    def test_setitem(self):

        # Temp Set Function
        def set_item(d, key, val):
            d[key] = val

        # Create Object Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create Object
        d = copy.deepcopy(DUMMY_TESTDICT)
        obj = self.HashFactory.from_new(d, key=k)

        # Test Keys
        for key in d:
            val = d[key] + "_updated"
            obj[key] = val
            self.assertEqual(val, obj[key])


class RedisTSHashTestCase(BackendRedisTestCase):

    def setUp(self):
        super(RedisTSHashTestCase, self).setUp()

        self.TSHashFactory = backend.PrefixedFactory(backend.TSHash)

    def tearDown(self):
        super(RedisTSHashTestCase, self).tearDown()

    def test_from_new(self):

        # Test Empty Dict w/o Key
        data = {}
        obj = self.TSHashFactory.from_new(data)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}".format(self.TSHashFactory.cls.__name__).lower())
        self.assertSubset(data, obj.get_dict())

        # Test Empty Dict w/ Key
        data = {}
        key = "testkey_1"
        obj = self.TSHashFactory.from_new(data, key=key)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{}+{}".format(self.TSHashFactory.cls.__name__, key).lower())
        self.assertSubset(data, obj.get_dict())
        self.assertEqual(obj['created_time'], obj['modified_time'])

        # Test Non-Empty Dict w/o Key
        data = DUMMY_TESTDICT
        self.assertRaises(backend.PersistentObjectError, self.TSHashFactory.from_new, data)

        # Test Non-Empty Dict w/ Key
        key = "testkey_2"
        data = copy.deepcopy(DUMMY_TESTDICT)
        obj = self.TSHashFactory.from_new(data, key=key)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{}+{}".format(self.TSHashFactory.cls.__name__, key).lower())
        self.assertSubset(data, obj.get_dict())
        self.assertEqual(obj['created_time'], obj['modified_time'])

    def test_set_dict(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create and Get Object
        d = copy.deepcopy(DUMMY_TESTDICT)
        h = self.TSHashFactory.from_new(d, key=k)
        self.assertSubset(d, h.get_dict())
        ct0 = float(h['created_time'])
        mt0 = float(h['modified_time'])
        self.assertEqual(ct0, mt0)

        # Update and Get Object
        time.sleep(0.01)
        d = copy.deepcopy(DUMMY_TESTDICT)
        for k in d:
            d[k] = "set_dict_test_val_{:s}".format(k)
        self.assertNotEqual(d, DUMMY_TESTDICT)
        h.set_dict(d)
        self.assertSubset(d, h.get_dict())
        ct1 = float(h['created_time'])
        mt1 = float(h['modified_time'])
        self.assertEqual(ct0, ct1)
        self.assertTrue(ct1 < mt1)
        self.assertTrue(mt0 < mt1)

    def test_setitem(self):

        # Temp Set Function
        def set_item(d, key, val):
            d[key] = val

        # Create Object Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create Object
        d = copy.deepcopy(DUMMY_TESTDICT)
        h = self.TSHashFactory.from_new(d, key=k)
        self.assertSubset(d, h.get_dict())
        ct0 = float(h['created_time'])
        mt0 = float(h['modified_time'])
        self.assertEqual(ct0, mt0)

        # Test Keys
        for key in d:
            time.sleep(0.01)
            val = d[key] + "_updated"
            h[key] = val
            self.assertEqual(val, h[key])
            ct1 = float(h['created_time'])
            mt1 = float(h['modified_time'])
            self.assertEqual(ct0, ct1)
            self.assertTrue(ct1 < mt1)
            self.assertTrue(mt0 < mt1)
            mt0 = mt1


class RedisUUIDHashTestCase(BackendRedisTestCase):

    def setUp(self):
        super(RedisUUIDHashTestCase, self).setUp()

        self.UUIDHashFactory = backend.UUIDFactory(backend.Hash)

    def tearDown(self):
        super(RedisUUIDHashTestCase, self).tearDown()

    def test_from_new(self):

        # Test Empty Dict
        d = {}
        self.assertRaises(ValueError, self.UUIDHashFactory.from_new, d)

        # Test Non-Empty Dict w/o Key
        d = copy.deepcopy(DUMMY_TESTDICT)
        h = self.UUIDHashFactory.from_new(d)
        self.assertSubset(d, h.get_dict())

    def test_from_existing(self):

        k = uuid.UUID("01c47915-4777-11d8-bc70-0090272ff725")

        # Test Non-Existant Object
        self.assertRaises(backend.ObjectDNE, self.UUIDHashFactory.from_existing, k)

        # Test Existing Object
        d = copy.deepcopy(DUMMY_TESTDICT)
        h1 = self.UUIDHashFactory.from_new(d)
        self.assertSubset(d, h1.get_dict())
        h2 = self.UUIDHashFactory.from_existing(h1.obj_key)
        self.assertEqual(h1, h2)
        self.assertEqual(h1.get_dict(), h2.get_dict())


class RedisSetTestCase(BackendRedisTestCase):

    def setUp(self):
        super(RedisSetTestCase, self).setUp()

        self.SetFactory = backend.PrefixedFactory(backend.Set)

    def tearDown(self):
        super(RedisSetTestCase, self).tearDown()

    def test_from_new(self):

        # Create Key
        key = "testkey"

        # Test Empty Set w/o Key
        v = set([])
        self.assertRaises(ValueError, self.SetFactory.from_new, v)

        # Test Empty Dict w/ Key
        v = set([])
        self.assertRaises(ValueError, self.SetFactory.from_new, v, key=key)

        # Test Non-Empty Dict w/o Key
        v = set(['a', 'b', 'c'])
        obj = self.SetFactory.from_new(v)
        self.assertTrue(obj)
        self.assertEquals(obj.full_key, "{:s}".format(self.SetFactory.cls.__name__).lower())

        # Test Non-Empty Dict w/ Key
        v = set(['a', 'b', 'c'])
        obj = self.SetFactory.from_new(v, key=key)
        self.assertEquals(obj.full_key, "{:s}+{:s}".format(self.SetFactory.cls.__name__, key).lower())
        self.assertEqual(v, obj.get_set())

    def test_from_existing(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Test Non-Existant Object
        self.assertRaises(backend.ObjectDNE, self.SetFactory.from_existing, key=k)

        # Test Existing Object
        v = set(['a', 'b', 'c'])
        s1 = self.SetFactory.from_new(v, key=k)
        self.assertEqual(v, s1.get_set())
        s2 = self.SetFactory.from_existing(key=k)
        self.assertEqual(s1, s2)
        self.assertEqual(s1.get_set(), s2.get_set())

    def test_from_raw(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Test Non-Existant Object
        v = set(['a', 'b', 'c'])
        s1 = self.SetFactory.from_raw(key=k)
        self.assertFalse(s1.get_set())
        s1.add_vals(v)
        self.assertEqual(v, s1.get_set())

        # Test Existing Object
        s2 = self.SetFactory.from_raw(key=k)
        self.assertEqual(v, s2.get_set())

        # Compare Objects
        self.assertEqual(s1, s2)
        self.assertEqual(s1.get_set(), s2.get_set())

    def test_get_set(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create and get set
        v = set(['a', 'b', 'c'])
        s = self.SetFactory.from_new(v, key=k)
        self.assertEqual(v, s.get_set())

    def test_add_vals(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create and get set
        v1 = set(['a', 'b', 'c'])
        s = self.SetFactory.from_new(v1, key=k)
        self.assertEqual(v1, s.get_set())

        # Add New Vals
        v2 = set(['d', 'e'])
        s.add_vals(v2)
        self.assertEqual((v1 | v2), s.get_set())

        # Add Existing Vals
        v3 = set(['d', 'e'])
        s.add_vals(v3)
        self.assertEqual((v1 | v2 | v3), s.get_set())

    def test_del_vals(self):

        # Create Key
        k = "testkey_{:03d}".format(random.randint(0, 999))

        # Create and get set
        v1 = set(['a', 'b', 'c', 'd', 'e'])
        s = self.SetFactory.from_new(v1, key=k)
        self.assertEqual(v1, s.get_set())

        # Remove Existing Vals
        v2 = set(['d', 'e'])
        self.assertEqual(s.del_vals(v2), len(v2))
        self.assertEqual((v1 - v2), s.get_set())

        # Remove Existing Vals
        v3 = set(['d', 'e'])
        self.assertEqual(s.del_vals(v3), 0)
        self.assertEqual((v1 - v2 - v3), s.get_set())


class RedisUUIDSetTestCase(BackendRedisTestCase):

    def setUp(self):
        super(RedisUUIDSetTestCase, self).setUp()

        self.UUIDSetFactory = backend.UUIDFactory(backend.Set)

    def tearDown(self):
        super(RedisUUIDSetTestCase, self).tearDown()

    def test_from_new(self):

        # Test Empty Set
        v = set([])
        self.assertRaises(ValueError, self.UUIDSetFactory.from_new, v)

        # Test Non-Empty Dict w/o Key
        v = set(['a', 'b', 'c'])
        s = self.UUIDSetFactory.from_new(v)
        self.assertSubset(v, s.get_set())

    def test_from_existing(self):

        k = uuid.UUID("01c47915-4777-11d8-bc70-0090272ff725")

        # Test Non-Existant Object
        self.assertRaises(backend.ObjectDNE, self.UUIDSetFactory.from_existing, k)

        # Test Existing Object
        v = set(['a', 'b', 'c'])
        s1 = self.UUIDSetFactory.from_new(v)
        self.assertSubset(v, s1.get_set())
        s2 = self.UUIDSetFactory.from_existing(s1.obj_key)
        self.assertEqual(s1, s2)
        self.assertEqual(s1.get_set(), s2.get_set())


### Main ###
if __name__ == '__main__':
    unittest.main()
