Description
===========

Extmemcached is extending of base memcached cache backend for Django with simple way of
avoiding Thundering Herd problem

It's provide method get_or_set that allow to avoid Thundering Herd problem in most simple way
Example:

.. code-block:: python

    some_params = {'something': 10}
    cached_value = cache.get_or_set(some_key, cllable_function, callback_params=some_params)
..

Method will try to retrieve data from cache and if it's empty - the callable
object with parameters will be used for getting needed data and also stored to cache as well.
To avoiding Thundering Herd problem during operation method using lock with atomic memcached operation ADD.
After all operations - lock is released.
If lock already exist - method will wait until it will be released and  the cached data will be returned



How to install
--------------

Run ``python setup.py install`` to install,
or place ``django-extmemcachedcache`` on your Python path.


Configure as cache backend
--------------------------

Cache binding using python-memcached:

.. code-block:: python

    CACHES = {
        "default": {
            "BACKEND": "extmemcachedcache.ExtMemcachedCache",
            "LOCATION": "127.0.0.1:11211",
        }
    }
..

cache binding using pylibmc:

.. code-block:: python

    CACHES = {
        "default": {
            "BACKEND": "extmemcachedcache.ExtPyLibMCCache",
            "LOCATION": "127.0.0.1:11211",
        }
    }
..

Configuration
-------------
The time for lock waiting could be configured with variable `CACHE_HERD_LOCK_TIMEOUT`
by default it's 60 seconds

