itsdangerous
============

.. module:: itsdangerous

Sometimes you just want to send some data to untrusted environments.  But
how to do this?  The trick involves signing.  Given a key only you know
and some random data, you can cryptographically sign them and, hand it
over to someone else, and when you get the data back you can easily ensure
that nobody tampered with it.

Granted, the receiver can decode the contents and look into the package,
but they can not modify the contents unless they also have your secret
key.  So if you keep the key secret and complex, you will be fine.

Internally it uses HMAC and SHA1 for signing and bases the implementation
on the `Django signing module
<https://docs.djangoproject.com/en/dev/topics/signing/>`_.  The library is
BSD licensed and written by Armin Ronacher though most of the copyright
for the design and implementation goes to Simon Willison and the other
amazing Django people that made this library possible.

Signing Interface
-----------------

The most basic interface is the signing interface.  With :class:`Signer`
can be used to attach a signature to a specific string:

>>> from itsdangerous import Signer
>>> s = Signer('secret-key')
>>> s.sign('my string')
'my string.wh6tMHxLgJqB6oY1uT73iMlyrOA'
    
The signature is appended to the string, separated by a dot (``.``).  To
validate the string, use the :meth:`~Signer.unsign` method:

>>> s.unsign('my string.wh6tMHxLgJqB6oY1uT73iMlyrOA')
'my string'

If unicode strings are provided, an implicit encoding to utf-8 happens.
However after unsigning you don't be able to tell if it was unicode or
a bytestring.

If the unsining fails you will get an exception:

>>> s.unsign('my string.wh6tMHxLgJqB6oY1uT73iMlyrOX')
Traceback (most recent call last):
  ...
itsdangerous.BadSignature: Signature "wh6tMHxLgJqB6oY1uT73iMlyrOX" does not match

Signatures with Timestamps
--------------------------

If you want to expire signatures you can use the :class:`TimestampSigner`
which will additionally put a timestamp information in and sign this.
On unsigning you can validate if the timestamp did not expire:

>>> from itsdangerous import TimestampSigner
>>> s = TimestampSigner('secret-key')
>>> string = s.sign('foo')
>>> s.unsign(string, max_age=5)
Traceback (most recent call last):
  ...
itsdangerous.SignatureExpired: Signature age 15 > 5 seconds

Serialization
-------------

Because strings are hard to handle this module also provides a
serilization interface similar to json/pickle and others.  Internally
it does in fact use simplejson by default which however can be changed
if you subclass.  The :class:`Serializer` class implements that:

>>> from itsdangerous import Serializer
>>> s = Serializer('secret-key')
>>> s.dumps([1, 2, 3, 4])
'[1, 2, 3, 4].r7R9RhGgDPvvWl3iNzLuIIfELmo'

And it can of course also load:

>>> s.loads('[1, 2, 3, 4].r7R9RhGgDPvvWl3iNzLuIIfELmo')
[1, 2, 3, 4]

If you want to have the timestamp attached you can use the
:class:`TimedSerializer`.

URL Safe Serialization
----------------------

Often it is helpful if you can pass these trusted strings to environments
where you only have a limited set of characters available.  Because of
this, itsdangerous also provides URL safe serializers:

>>> from itsdangerous import URLSafeSerializer
>>> s = URLSafeSerializer('secret-key')
>>> s.dumps([1, 2, 3, 4])
'WzEsMiwzLDRd.wSPHqC0gR7VUqivlSukJ0IeTDgo'
>>> s.loads('WzEsMiwzLDRd.wSPHqC0gR7VUqivlSukJ0IeTDgo')
[1, 2, 3, 4]

API
---

Signers
~~~~~~~

.. autoclass:: Signer
   :members:

.. autoclass:: TimestampSigner
   :members:

Serializers
~~~~~~~~~~~

.. autoclass:: Serializer
   :members:

.. autoclass:: TimedSerializer
   :members:

.. autoclass:: URLSafeSerializer

.. autoclass:: URLSafeTimedSerializer

Exceptions
~~~~~~~~~~

.. autoexception:: BadSignature

.. autoexception:: SignatureExpired

Useful Helpers
~~~~~~~~~~~~~~

.. autoexception:: SignatureExpired

.. autofunction:: base64_encode

.. autofunction:: base64_decode
