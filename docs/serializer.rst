.. module:: itsdangerous.serializer

Serialization Interface
=======================

The :doc:`/signer` only signs strings. To sign other types, the
:class:`Serializer` class provides a ``dumps``/``loads`` interface
similar to Python's :mod:`json` module, which serializes the object to a
string then signs that.

Use :meth:`~Serializer.dumps` to serialize and sign the data:

.. code-block:: python

    from itsdangerous.serializer import Serializer
    s = Serializer("secret-key")
    s.dumps([1, 2, 3, 4])
    b'[1, 2, 3, 4].r7R9RhGgDPvvWl3iNzLuIIfELmo'

Use :meth:`~Serializer.loads` to verify the signature and deserialize
the data.

.. code-block:: python

    s.loads('[1, 2, 3, 4].r7R9RhGgDPvvWl3iNzLuIIfELmo')
    [1, 2, 3, 4]

By default, data is serialized to JSON. If simplejson is installed, it
is preferred over the built-in :mod:`json` module. This internal
serializer can be changed by subclassing.

To record and validate the age of the signature, see :doc:`/timed`.
To serialize to a format that is safe to use in URLs, see
:doc:`/url_safe`.


.. _the-salt:

The Salt
--------

All classes also accept a salt argument. The name might be misleading
because usually if you think of salts in cryptography you would expect
the salt to be something that is stored alongside the resulting signed
string as a way to prevent rainbow table lookups. Such salts are usually
public.

In itsdangerous, like in the original Django implementation, the salt
serves a different purpose. You could describe it as namespacing. It's
still not critical if you disclose it because without the secret key it
does not help an attacker.

Let's assume that you have two links you want to sign. You have the
activation link on your system which can activate a user account and you
have an upgrade link that can upgrade a user's account to a paid account
which you send out via email. If in both cases all you sign is the user
ID a user could reuse the variable part in the URL from the activation
link to upgrade the account. Now you could either put more information
in there which you sign (like the intention: upgrade or activate), but
you could also use different salts:

.. code-block:: python

    from itsdangerous.url_safe import URLSafeSerializer
    s1 = URLSafeSerializer("secret-key", salt="activate")
    s1.dumps(42)
    'NDI.MHQqszw6Wc81wOBQszCrEE_RlzY'
    s2 = URLSafeSerializer("secret-key", salt="upgrade")
    s2.dumps(42)
    'NDI.c0MpsD6gzpilOAeUPra3NShPXsE'

The second serializer can't load data dumped with the first because the
salts differ:

.. code-block:: python

    s2.loads(s1.dumps(42))
    Traceback (most recent call last):
      ...
    itsdangerous.exc.BadSignature: Signature "MHQqszw6Wc81wOBQszCrEE_RlzY" does not match

Only the serializer with the same salt can load the data:

.. code-block:: python

    s2.loads(s2.dumps(42))
    42


Responding to Failure
---------------------

Exceptions have helpful attributes which allow you to inspect the
payload if the signature check failed. This has to be done with extra
care because at that point you know that someone tampered with your data
but it might be useful for debugging purposes.

.. code-block:: python

    from itsdangerous.serializer import Serializer
    from itsdangerous.exc import BadSignature, BadData

    s = URLSafeSerializer("secret-key")
    decoded_payload = None

    try:
        decoded_payload = s.loads(data)
        # This payload is decoded and safe
    except BadSignature as e:
        if e.payload is not None:
            try:
                decoded_payload = s.load_payload(e.payload)
            except BadData:
                pass
            # This payload is decoded but unsafe because someone
            # tampered with the signature. The decode (load_payload)
            # step is explicit because it might be unsafe to unserialize
            # the payload (think pickle instead of json!)

If you don't want to inspect attributes to figure out what exactly went
wrong you can also use :meth:`~Serializer.loads_unsafe`:

.. code-block:: python

    sig_okay, payload = s.loads_unsafe(data)

The first item in the returned tuple is a boolean that indicates if the
signature was correct.

API
---

.. autoclass:: Serializer
    :members:
