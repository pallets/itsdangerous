.. module:: itsdangerous.timed

Signing With Timestamps
=======================

If you want to expire signatures you can use the
:class:`TimestampSigner` class which adds timestamp information and
signs it. On unsigning you can validate that the timestamp is not older
than a given age.

.. code-block:: python

    from itsdangerous import TimestampSigner
    s = TimestampSigner('secret-key')
    string = s.sign('foo')

.. code-block:: python

    s.unsign(string, max_age=5)
    Traceback (most recent call last):
      ...
    itsdangerous.exc.SignatureExpired: Signature age 15 > 5 seconds

If desired, for example when testing code that triggers on
SignatureExpired errors you can specify the timestamp used when
signing,

.. code-block:: python

    from itsdangerous import TimestampSigner
    ts = int(datetime(2021, 7, 29, 10, 45).timestamp())
    s = TimestampSigner('secret-key', timestamp=ts)
    string = s.sign('foo')

.. autoclass:: TimestampSigner
    :members:

.. autoclass:: TimedSerializer
    :members:
