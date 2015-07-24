import pickle
from time import sleep

from django.conf import settings
from django.core.cache.backends.memcached import BaseMemcachedCache, DEFAULT_TIMEOUT
from django.utils.functional import cached_property


#: Herd timeout, by default it's 60s
CACHE_HERD_LOCK_TIMEOUT = getattr(settings, 'CACHE_HERD_LOCK_TIMEOUT', 60)


class BaseExtMemcachedCache(BaseMemcachedCache):
    """
    Extending of base memcached cache with simple way of of avoiding Thundering Herd
    """

    #: Sleep time for herd lock - 100ms
    _HERD_SLEEP_TIME = 0.1

    def __init__(self, *args, **kwargs):
        super(BaseExtMemcachedCache, self).__init__(*args, **kwargs)

    def get_or_set(self, key, callback, callback_params={}, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Retrieving cached value or calling callback object to store it

        :param key: Key
        :param callback: Callable object that will be used for retrieving data for caching
        :param callback_params: Parameters that should be passed to callable object
        :return: Cached object
        """

        if not callable(callback):
            raise ValueError("Callback parameter is not callable")

        lock_key = "%s_herd_lock" % key

        # ADD is atomic operation that return True on success nad False if value already exist
        # if there some lock - we should waite
        while not self.add(lock_key, 1, timeout=CACHE_HERD_LOCK_TIMEOUT, version=version):
            # Sleep for 100ms
            sleep(self._HERD_SLEEP_TIME)

        result = self.get(key, version=version)
        if result is not None:
            self.delete(lock_key, version=version)
            return result

        try:
            result = callback(**callback_params)
        except Exception:
            self.delete(lock_key)
            raise

        if result is None:
            return result

        self.set(key, result, timeout)
        self.delete(lock_key)
        return result


class ExtMemcachedCache(BaseExtMemcachedCache):
    """
    An implementation of a cache binding using python-memcached
    """

    def __init__(self, server, params):
        import memcache
        super(ExtMemcachedCache, self).__init__(server, params,
                                                library=memcache,
                                                value_not_found_exception=ValueError)

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers, pickleProtocol=pickle.HIGHEST_PROTOCOL)
        return self._client


class ExtPyLibMCCache(BaseExtMemcachedCache):
    """
    An implementation of a cache binding using pylibmc
    """

    def __init__(self, server, params):
        import pylibmc
        super(ExtPyLibMCCache, self).__init__(server, params,
                                              library=pylibmc,
                                              value_not_found_exception=pylibmc.NotFound)

    @cached_property
    def _cache(self):
        client = self._lib.Client(self._servers)
        if self._options:
            client.behaviors = self._options

        return client
