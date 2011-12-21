"""
afraid
------

This is a simple & extensible command-line client for the dynamic DNS service
offered by `afraid.org <http://freedns.afraid.org/>`_. It will retrieve the set
of hostnames associated with a particular account and update their records at
a user-specifiable regular interval.

The development version is available at `GitHub
<https://github.com/atdt/afraid>`_. Issues should be documented
there.
"""
from distutils.core import setup

setup(
    name='afraid',
    version='0.1-dev',
    license='ISC',
    author='Ori Livneh',
    author_email='ori.livneh@gmail.com',
    description='A simple client for the afraid.org dynamic DNS service',
    long_description=__doc__,
    packages=['afraid'],
    entry_points={
        'console_scripts': [
            'afraid = afraid:main',
        ],
    },
    test_suite = 'afraid.test_afraid.suite',
)
