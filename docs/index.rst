itsdangerous
============

.. module:: itsdangerous

Sometimes you just want to send some data to untrusted environments.  But
how to do this safely?  The trick involves signing.  Given a key only you
know, you can cryptographically sign your data and hand it over to someone
else.  When you get the data back you can easily ensure that nobody tampered
with it.

Granted, the receiver can decode the contents and look into the package,
but they can not modify the contents unless they also have your secret
key.  So if you keep the key secret and complex, you will be fine.

Internally itsdangerous uses HMAC and SHA1 for signing by default and bases the
implementation on the `Django signing module
<https://docs.djangoproject.com/en/dev/topics/signing/>`_.  It also
however supports JSON Web Signatures (JWS).  The library is BSD licensed and
written by Armin Ronacher though most of the copyright for the design and
implementation goes to Simon Willison and the other amazing Django people
that made this library possible.

Installation
------------

You can get the library directly from PyPI::

    pip install itsdangerous

Example Use Cases
-----------------

-   You can serialize and sign a user ID for unsubscribing of newsletters
    into URLs.  This way you don't need to generate one-time tokens and
    store them in the database.  Same thing with any kind of activation
    link for accounts and similar things.
-   Signed objects can be stored in cookies or other untrusted sources
    which means you don't need to have sessions stored on the server, which
    reduces the number of necessary database queries.
-   Signed information can safely do a roundtrip between server and client
    in general which makes them useful for passing server-side state to a
    client and then back.

Signing Interface
-----------------

The most basic interface is the signing interface.  The :class:`Signer` class
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
However after unsigning you won't be able to tell if it was unicode or
a bytestring.

If the unsigning fails you will get an exception:

>>> s.unsign('my string.wh6tMHxLgJqB6oY1uT73iMlyrOX')
Traceback (most recent call last):
  ...
itsdangerous.BadSignature: Signature "wh6tMHxLgJqB6oY1uT73iMlyrOX" does not match

Signatures with Timestamps
--------------------------

If you want to expire signatures you can use the :class:`TimestampSigner`
class which will additionally put in a timestamp information and sign it.
On unsigning you can validate that the timestamp did not expire:

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
serialization interface similar to json/pickle and others.  (Internally
it uses simplejson by default, however this can be changed by subclassing.)
The :class:`Serializer` class implements that:

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

JSON Web Signatures
-------------------

Starting with “itsdangerous” 0.18 JSON Web Signatures are also supported.
They generally work very similar to the already existing URL safe
serializer but will emit headers according to the current draft (10) of
the JSON Web Signature (JWS) [``draft-ietf-jose-json-web-signature``].

>>> from itsdangerous import JSONWebSignatureSerializer
>>> s = JSONWebSignatureSerializer('secret-key')
>>> s.dumps({'x': 42})
'eyJhbGciOiJIUzI1NiJ9.eyJ4Ijo0Mn0.ZdTn1YyGz9Yx5B5wNpWRL221G1WpVE5fPCPKNuc6UAo'

When loading the value back the header will not be returned by default
like with the other serializers.  However it is possible to also ask for
the header by passing ``return_header=True``.
Custom header fields can be provided upon serialization:

>>> s.dumps(0, header_fields={'v': 1})
'eyJhbGciOiJIUzI1NiIsInYiOjF9.MA.wT-RZI9YU06R919VBdAfTLn82_iIQD70J_j-3F4z_aM'
>>> s.loads('eyJhbGciOiJIUzI1NiIsInYiOjF9.MA.wT-RZI9YU06R919VBdAf'
...         'TLn82_iIQD70J_j-3F4z_aM', return_header=True)
...
(0, {u'alg': u'HS256', u'v': 1})

“itsdangerous” only provides HMAC SHA derivatives and the none algorithm
at the moment and does not support the ECC based ones.  The algorithm in
the header is checked against the one of the serializer and on a mismatch
a :exc:`BadSignature` exception is raised.

.. _the-salt:

The Salt
--------

All classes also accept a salt argument.  The name might be misleading
because usually if you think of salts in cryptography you would expect the
salt to be something that is stored alongside the resulting signed string
as a way to prevent rainbow table lookups.  Such salts are usually public.

In “itsdangerous”, like in the original Django implementation, the salt
serves a different purpose.  You could describe it as namespacing.  It's
still not critical if you disclose it because without the secret key it
does not help an attacker.

Let's assume that you have two links you want to sign.  You have the
activation link on your system which can activate a user account and then
you have an upgrade link that can upgrade a user's account to a paid
account which you send out via email.  If in both cases all you sign is
the user ID a user could reuse the variable part in the URL from the
activation link to upgrade the account.  Now you could either put more
information in there which you sign (like the intention: upgrade or
activate), but you could also use different salts:

>>> s1 = URLSafeSerializer('secret-key', salt='activate-salt')
>>> s1.dumps(42)
'NDI.kubVFOOugP5PAIfEqLJbXQbfTxs'
>>> s2 = URLSafeSerializer('secret-key', salt='upgrade-salt')
>>> s2.dumps(42)
'NDI.7lx-N1P-z2veJ7nT1_2bnTkjGTE'
>>> s2.loads(s1.dumps(42))
Traceback (most recent call last):
  ...
itsdangerous.BadSignature: Signature "kubVFOOugP5PAIfEqLJbXQbfTxs" does not match

Only the serializer with the same salt can load the value:

>>> s2.loads(s2.dumps(42))
42

Responding to Failure
---------------------

Starting with itsdangerous 0.14 exceptions have helpful attributes which
allow you to inspect payload if the signature check failed.  This has to
be done with extra care because at that point you know that someone
tampered with your data but it might be useful for debugging purposes.

Example usage::

    from itsdangerous import URLSafeSerializer, BadSignature, BadData
    s = URLSafeSerializer('secret-key')
    decoded_payload = None
    try:
        decoded_payload = s.loads(data)
        # This payload is decoded and safe
    except BadSignature, e:
        encoded_payload = e.payload
        if encoded_payload is not None:
            try:
                decoded_payload = s.load_payload(encoded_payload)
            except BadData:
                pass
            # This payload is decoded but unsafe because someone
            # tampered with the signature.  The decode (load_payload)
            # step is explicit because it might be unsafe to unserialize
            # the payload (think pickle instead of json!)

If you don't want to inspect attributes to figure out what exactly went
wrong you can also use the unsafe loading::

    from itsdangerous import URLSafeSerializer
    s = URLSafeSerializer('secret-key')
    sig_okay, payload = s.loads_unsafe(data)

The first item in the returned tuple is a boolean that indicates if the
signature was correct.

Python 3 Notes
--------------

On Python 3 the interface that itsdangerous provides can be confusing at
first.  Depending on the internal serializer it wraps the return value of
the functions can alter between unicode strings or bytes objects.  The
internal signer is always byte based.

This is done to allow the module to operate on different serializers
independent of how they are implemented.  The module decides on the
type of the serializer by doing a test serialization of an empty object.


.. include:: ../CHANGES

API
---

Signers
~~~~~~~

.. autoclass:: Signer
   :members:

.. autoclass:: TimestampSigner
   :members:

Signing Algorithms
~~~~~~~~~~~~~~~~~~

.. autoclass:: NoneAlgorithm

.. autoclass:: HMACAlgorithm

Serializers
~~~~~~~~~~~

.. autoclass:: Serializer
   :members:

.. autoclass:: TimedSerializer
   :members:

.. autoclass:: JSONWebSignatureSerializer
   :members:

.. autoclass:: TimedJSONWebSignatureSerializer
   :members:

.. autoclass:: URLSafeSerializer

.. autoclass:: URLSafeTimedSerializer

Exceptions
~~~~~~~~~~

.. autoexception:: BadData
   :members:

.. autoexception:: BadSignature
   :members:

.. autoexception:: BadTimeSignature
   :members:

.. autoexception:: SignatureExpired
   :members:

.. autoexception:: BadHeader
   :members:

.. autoexception:: BadPayload
   :members:

Useful Helpers
~~~~~~~~~~~~~~

.. autofunction:: base64_encode

.. autofunction:: base64_decode
