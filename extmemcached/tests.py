from time import sleep
from multiprocessing.pool import ThreadPool

from django.conf import settings
from django.core.cache import caches
from django.test import SimpleTestCase


class TestExtCatch(SimpleTestCase):
    """
    In case if some of ExtMemcached backed in use - it can be tested
    """

    _test_key = 'ext_memcached_test_key'
    _caches_to_test = []

    def setUp(self):
        if self._caches_to_test:
            # We don't need to collect them any more
            return

        for alias, params in settings.CACHES.iteritems():
            backend = params.get('BACKEND', '')
            if 'ExtMemcachedCache' in backend or 'ExtPyLibMCCache' in backend:
                self._caches_to_test.append(caches[alias])

    def tearDown(self):
        # We should remove all test data from caches
        for cache in self._caches_to_test:
            cache.delete(self._test_key)

    def test_simple_actions(self):
        """
        Test for checking main functionality of cache
        """
        for cache in self._caches_to_test:
            cache.get_or_set(self._test_key, lambda v: v, {'v': 1})
            self.assertEqual(cache.get(self._test_key), 1, cache)

    def test_negative(self):
        """
        Exception should appear
        """
        not_callable = ''
        for cache in self._caches_to_test:
            with self.assertRaises(ValueError):
                cache.get_or_set(self._test_key, not_callable, {'value': 1}, cache)

    def test_lock_release(self):
        """
        Test that in case of exception - lock will be released
        """
        def test_callable(v):
            raise Exception(v)

        for cache in self._caches_to_test:
            with self.assertRaises(Exception):
                cache.get_or_set(self._test_key, test_callable, {'v': 1})

            self.assertEqual(cache.get("%s_herd_lock" % self._test_key), None)

    def test_empty_result(self):
        """
        Test empty result that shouldn't be stored in memcached
        """
        for cache in self._caches_to_test:
            cache.get_or_set(self._test_key, lambda: None)
            add_result = cache.add(self._test_key, 1)

            # If key do not exist in memcached - it will be created and ADD
            # operation should return True
            self.assertEqual(add_result, True)

    # Things below could be implemented much easier with mock

    def _test_herd_management(self, catch):
        globals()['call_count'] = 0

        def test_callable(v):
            global call_count
            call_count += 1

            sleep(0.1)
            return v

        pool = ThreadPool(processes=10)
        processes = []
        for _ in xrange(10):
            to_func = {
                'key': self._test_key,
                'callback': test_callable,
                'callback_params': {'v': 17},
            }

            async_result = pool.apply_async(
                catch.get_or_set, kwds=to_func
            )
            processes.append(async_result)

        results = []
        for thread in processes:
            thread.wait()
            results.append(thread.get())

        # Checking that callable method was applied only once
        self.assertEqual(globals()['call_count'], 1)

        # Checking results - they all should be the same
        self.assertEqual(results, [17] * 10)

    def test_herd_management(self):
        """
        Test for checking main functionality of cache
        """
        for cache in self._caches_to_test:
            self._test_herd_management(cache)
