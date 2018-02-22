#!/usr/bin/env python
import os
import re
from setuptools import setup

setup_dir = os.path.dirname(__file__)

with open(os.path.join(setup_dir, 'itsdangerous.py'), 'rb') as f:
    version = re.search(r'^__version__ = \'(\d+\.(?:\d+\.)*\d+)\'', f.read().decode('utf8'), re.M).group(1)

setup(
    name='itsdangerous',
    version=version,
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    url='https://github.com/pallets/itsdangerous',
    description='Various helpers to pass trusted data to untrusted environments and back.',
    py_modules=['itsdangerous'],
    python_requires='>=2.6,!=3.0.*,!=3.1.*,!=3.2.*',
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent'
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
