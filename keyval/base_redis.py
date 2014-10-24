# -*- coding: utf-8 -*-

# Andy Sayler
# Fall 2014
# Univerity of Colorado


import redis

import base
import base_abc

class Driver(redis.StrictRedis):

    pass


class String(base_abc.String):

    @classmethod
    def from_new(cls, driver, key, val, *args, **kwargs):
        """New Constructor"""

        # Call Parent
        obj = super(String, cls).from_new(driver, key, *args, **kwargs)

        # Check Existence
        if obj.exists():
            raise base.ObjectExists(obj)

        # Create Object
        obj.driver.set(obj.key, val)

        # Return Object
        return obj

    @classmethod
    def from_existing(cls, driver, key, *args, **kwargs):
        """Existing Constructor"""

        # Call Parent
        obj = super(String, cls).from_existing(driver, key, *args, **kwargs)

        # Check Existence
        if not obj.exists():
            raise base.ObjectDNE(obj)

        # Return Object
        return obj

    def val(self):
        """Get Value as Corresponding Python Object"""

        # Get Object
        return obj.driver.get(obj.key)

    def rem(self):
        """Delete Object"""

        # Delete Object
        if not self.driver.delete(self.key):
            raise base.PersistentObjectError("Delete Failed")

        # Call Parent
        super(StringObject, self).delete()

    def exists(self):
        """Check if Object Exists"""

        # Check Existence
        return self.driver.exists(self.key)

    def __len__(self):
        """Get Length of String"""

        # Get Length
        return self.driver.strlen(self.key)

    def __getitem__(self):
        """Iterate Values"""

        raise NotImplementedError()
