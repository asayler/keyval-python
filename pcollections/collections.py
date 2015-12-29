# -*- coding: utf-8 -*-


# Andy Sayler
# 2014, 2015
# pcollections Package


### Pylint ###


### Imports ###

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from future.utils import native_str
from future.utils import with_metaclass
from future.utils import python_2_unicode_compatible
from builtins import *

from . import backends


### Classes ###

class PCollections(object):

    ## Methods ##

    def __init__(self, backend):

        # Check Args
        if not isinstance(backend, backends.Backend):
            raise TypeError("backend must be instance of Backend")

        # Call Parent
        super().__init__()

        # Save Attrs
        self._backend = backend

    ## Properties ##

    @property
    def backend(self):
        return self._backend

    ## Objects ##

    def String(self, key, create=None, existing=None):
        return self.backend.module.String(self.backend.driver, key,
                                          create=create, existing=existing)
    def MutableString(self, key, create=None, existing=None):
        return self.backend.module.MutableString(self.backend.driver, key,
                                                 create=create, existing=existing)

    def List(self, key, create=None, existing=None):
        return self.backend.module.List(self.backend.driver, key,
                                        create=create, existing=existing)
    def MutableList(self, key, create=None, existing=None):
        return self.backend.module.MutableList(self.backend.driver, key,
                                               create=create, existing=existing)

    def Set(self, key, create=None, existing=None):
        return self.backend.module.Set(self.backend.driver, key,
                                       create=create, existing=existing)
    def MutableSet(self, key, create=None, existing=None):
        return self.backend.module.MutableSet(self.backend.driver, key,
                                              create=create, existing=existing)

    def Dictionary(self, key, create=None, existing=None):
        return self.backend.module.Dictionary(self.backend.driver, key,
                                              create=create, existing=existing)
    def MutableDictionary(self, key, create=None, existing=None):
        return self.backend.module.MutableDictionary(self.backend.driver, key,
                                                     create=create, existing=existing)
