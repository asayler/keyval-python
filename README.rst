Python Persistent Collections ABC Interface
===========================================

By `Andy Sayler <https://www.andysayler.com>`_

About
-----

A persistent implementation of the `Python Collections Abstract Base
Classes <https://docs.python.org/2/library/collections.html#collections-abstract-base-classes>`_,
plus a few others.

Supports both Python 2.7 and Python 3.3+.

Status
------

.. image:: https://travis-ci.org/asayler/pcollections.svg?branch=master
   :target: https://travis-ci.org/asayler/pcollections

Completed Data Structures
^^^^^^^^^^^^^^^^^^^^^^^^^
* String (Sequence)
* MutableString (MutableSequence)
* List (Sequence)
* MutableList (MutableSequence)
* Set (Set)
* MutableSet (MutableSet)
* Dictionary (Mapping)
* MutableDictionary (MutableMapping)

Completed Flavors
^^^^^^^^^^^^^^^^^
* base - atomic reads
* atomic - atomic reads and writes

Completed Backends
^^^^^^^^^^^^^^^^^^
* Redis

Planned Backends
^^^^^^^^^^^^^^^^
* In Memory (?)
* SQL (?)
* Disk (?)

Providence
----------

Forked from COG-core at
https://github.com/asayler/COG/commit/68d1df183d33ca7c8ef4e26a72cfc0b231c4a805.

Licensing
---------

Copyright 2014, 2015 by Andy Sayler

This file is part of PCollections.

PCollections is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

PCollections is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with Python KeyVal (see COPYING).  If not, see
http://www.gnu.org/licenses/.
