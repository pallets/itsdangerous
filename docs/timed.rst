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

.. autoclass:: TimestampSigner
    :members:

.. autoclass:: TimedSerializer
    :members:
