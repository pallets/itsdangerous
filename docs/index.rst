.. rst-class:: hide-header

itsdangerous
============

.. image:: _static/itsdangerous-logo.png
    :align: center
    :target: https://palletsprojects.com/p/itsdangerous/

Sometimes you just want to send some data to untrusted environments.  But
how to do this safely?  The trick involves signing.  Given a key only you
know, you can cryptographically sign your data and hand it over to someone
else.  When you get the data back you can easily ensure that nobody tampered
with it.

Granted, the receiver can decode the contents and look into the package,
but they can not modify the contents unless they also have your secret
key.  So if you keep the key secret and complex, you will be fine.

Internally itsdangerous uses HMAC and SHA-512 for signing by default.
The initial implementation was inspired by `Django's signing module
<https://docs.djangoproject.com/en/dev/topics/signing/>`_. It also
supports JSON Web Signatures (JWS). The library is BSD licensed.


Installing
----------

Install and update using `pip`_:

.. code-block:: text

    pip install -U itsdangerous

.. _pip: https://pip.pypa.io/en/stable/quickstart/


Example Use Cases
-----------------

-   You can serialize and sign a user ID in a URL and email it to them
    to unsubscribe from a newsletter. This way you don't need to
    generate one-time tokens and store them in the database. Same thing
    with any kind of activation link for accounts and similar things.
-   Signed objects can be stored in cookies or other untrusted sources
    which means you don't need to have sessions stored on the server,
    which reduces the number of necessary database queries.
-   Signed information can safely do a roundtrip between server and
    client in general which makes them useful for passing server-side
    state to a client and then back.


Table of Contents
-----------------

.. toctree::

    signer
    serializer
    exceptions
    timed
    url_safe
    jws
    encoding
    license
    changes
