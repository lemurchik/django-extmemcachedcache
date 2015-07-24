Description
===========

Extmemcached is extending of base memcached cache backend for Django with simple way of
avoiding Thundering Herd

It's provide method get_or_set that allow to avoid Thundering Herd problem in most simple way
Example:

.. code-block:: python

    cahced_value = cache.get_or_set(some_key, some_value)
..


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

