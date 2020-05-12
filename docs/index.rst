.. rst-class:: hide-header

ItsDangerous
============

.. image:: _static/itsdangerous-logo.png
    :align: center
    :target: https://palletsprojects.com/p/itsdangerous/

Sometimes you want to send some data to untrusted environments, then get
it back later. To do this safely, the data must be signed to detect
changes.

Given a key only you know, you can cryptographically sign your data and
hand it over to someone else. When you get the data back you can ensure
that nobody tampered with it.

The receiver can see the data, but they can not modify it unless they
also have your key. So if you keep the key secret and complex, you will
be fine.


Installing
----------

Install and update using `pip`_:

.. code-block:: text

    pip install -U itsdangerous

.. _pip: https://pip.pypa.io/en/stable/quickstart/


Example Use Cases
-----------------

-   Sign a user ID in a URL and email it to them to unsubscribe from a
    newsletter. This way you don't need to generate one-time tokens and
    store them in the database. Same thing with any kind of activation
    link for accounts and similar things.
-   Signed objects can be stored in cookies or other untrusted sources
    which means you don't need to have sessions stored on the server,
    which reduces the number of necessary database queries.
-   Signed information can safely do a round trip between server and
    client in general which makes them useful for passing server-side
    state to a client and then back.


Table of Contents
-----------------

.. toctree::

    concepts
    serializer
    signer
    exceptions
    timed
    url_safe
    encoding
    license
    changes
