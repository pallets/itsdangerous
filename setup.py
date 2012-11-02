import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


kwargs = {}
if sys.version_info >= (3, ):
    kwargs['use_2to3'] = True
setup(
    name='itsdangerous',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    version='0.17',
    url='http://github.com/mitsuhiko/itsdangerous',
    py_modules=['itsdangerous'],
    description='Various helpers to pass trusted data to untrusted environments.',
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    **kwargs
)
