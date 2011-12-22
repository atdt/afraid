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
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

deps = [
    'requests>=0.8.6',
    'python-daemon>=1.5.5',
]

setup(
    name='afraid',
    version='0.1-dev',
    description='A simple client for the afraid.org dynamic DNS service',
    author='Ori Livneh',
    author_email='ori.livneh@gmail.com',
    license='ISC',
    long_description=__doc__,
    packages=['afraid'],
    entry_points={
        'console_scripts': [
            'afraid = afraid:main',
        ],
    },
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: System :: Systems Administration',
    ),
    install_requires=deps,
    test_suite = 'afraid.tests',
)
