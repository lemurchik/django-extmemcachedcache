import os

from setuptools import setup

VERSION = '0.1.0'

setup(
    name='django-extmemcachedcache',
    version=VERSION,
    packages=['extmemcached'],
    description='Improved memcached cache backend for Django',
    long_description=file(
        os.path.join(os.path.dirname(__file__), 'README.rst')
    ).read(),
    author='Vladyslav Bondar',
    author_email='vladyslav.e.bondar@gmail.com',
    license='BSD',
    url='https://github.com/lemurchik/django-extmemcachedcache',
    keywords='django cache memcached',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django',
        'Environment :: Web Environment',
    ]
)
