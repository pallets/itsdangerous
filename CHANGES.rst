Version 2.0.0
-------------

Unreleased

-   Drop support for Python 2 and 3.5.
-   JWS support (``JSONWebSignatureSerializer``,
    ``TimedJSONWebSignatureSerializer``) is deprecated. Use a dedicated
    JWS/JWT library such as authlib instead. :issue:`129`
-   Importing ``itsdangerous.json`` is deprecated. Import Python's
    ``json`` module instead. :pr:`152`
-   Simplejson is no longer used if it is installed. To use a different
    library, pass it as ``Serializer(serializer=...)``. :issue:`146`
-   ``datetime`` values are timezone-aware with ``timezone.utc``. Code
    using ``TimestampSigner.unsign(return_timestamp=True)`` or
    ``BadTimeSignature.date_signed`` may need to change. :issue:`150`
-   If a signature has an age less than 0, it will raise
    ``SignatureExpired`` rather than appearing valid. This can happen if
    the timestamp offset is changed. :issue:`126`
-   ``BadTimeSignature.date_signed`` is always a ``datetime`` object
    rather than an ``int`` in some cases. :issue:`124`
-   Added support for key rotation. A list of keys can be passed as
    ``secret_key``, oldest to newest. The newest key is used for
    signing, all keys are tried for unsigning. :pr:`141`
-   Removed the default SHA-512 fallback signer from
    ``default_fallback_signers``. :issue:`155`
-   Add type information for static typing tools. :pr:`186`


Version 1.1.0
-------------

Released 2018-10-26

-   Change default signing algorithm back to SHA-1. :pr:`113`
-   Added a default SHA-512 fallback for users who used the yanked 1.0.0
    release which defaulted to SHA-512. :pr:`114`
-   Add support for fallback algorithms during deserialization to
    support changing the default in the future without breaking existing
    signatures. :pr:`113`
-   Changed capitalization of packages back to lowercase as the change
    in capitalization broke some tooling. :pr:`113`


Version 1.0.0
-------------

Released 2018-10-18

YANKED

*Note*: This release was yanked from PyPI because it changed the default
algorithm to SHA-512. This decision was reverted in 1.1.0 and it remains
at SHA1.

-   Drop support for Python 2.6 and 3.3.
-   Refactor code from a single module to a package. Any object in the
    API docs is still importable from the top-level ``itsdangerous``
    name, but other imports will need to be changed. A future release
    will remove many of these compatibility imports. :pr:`107`
-   Optimize how timestamps are serialized and deserialized. :pr:`13`
-   ``base64_decode`` raises ``BadData`` when it is passed invalid data.
    :pr:`27`
-   Ensure value is bytes when signing to avoid a ``TypeError`` on
    Python 3. :issue:`29`
-   Add a ``serializer_kwargs`` argument to ``Serializer``, which is
    passed to ``dumps`` during ``dump_payload``. :pr:`36`
-   More compact JSON dumps for unicode strings. :issue:`38`
-   Use the full timestamp rather than an offset, allowing dates before
    2011. :issue:`46`

    To retain compatibility with signers from previous versions,
    consider using `this shim <https://github.com/pallets/itsdangerous
    /issues/120#issuecomment-456913331>`_ when unsigning.
-   Detect a ``sep`` character that may show up in the signature itself
    and raise a ``ValueError``. :issue:`62`
-   Use a consistent signature for keyword arguments for
    ``Serializer.load_payload`` in subclasses. :issue:`74`, :pr:`75`
-   Change default intermediate hash from SHA-1 to SHA-512. :pr:`80`
-   Convert JWS exp header to an int when loading. :pr:`99`


Version 0.24
------------

Released 2014-03-28

-   Added a ``BadHeader`` exception that is used for bad headers that
    replaces the old ``BadPayload`` exception that was reused in those
    cases.


Version 0.23
------------

Released 2013-08-08

-   Fixed a packaging mistake that caused the tests and license files to
    not be included.


Version 0.22
------------

Released 2013-07-03

-   Added support for ``TimedJSONWebSignatureSerializer``.
-   Made it possible to override the signature verification function to
    allow implementing asymmetrical algorithms.


Version 0.21
------------

Released 2013-05-26

-   Fixed an issue on Python 3 which caused invalid errors to be
    generated.


Version 0.20
------------

Released 2013-05-23

-   Fixed an incorrect call into ``want_bytes`` that broke some uses of
    ItsDangerous on Python 2.6.


Version 0.19
------------

Released 2013-05-21

-   Dropped support for 2.5 and added support for 3.3.


Version 0.18
------------

Released 2013-05-03

-   Added support for JSON Web Signatures (JWS).


Version 0.17
------------

Released 2012-08-10

-   Fixed a name error when overriding the digest method.


Version 0.16
------------

Released 2012-07-11

-   Made it possible to pass unicode values to ``load_payload`` to make
    it easier to debug certain things.


Version 0.15
------------

Released 2012-07-11

-   Made standalone ``load_payload`` more robust by raising one specific
    error if something goes wrong.
-   Refactored exceptions to catch more cases individually, added more
    attributes.
-   Fixed an issue that caused ``load_payload`` not work in some
    situations with timestamp based serializers
-   Added an ``loads_unsafe`` method.


Version 0.14
------------

Released 2012-06-29

-   API refactoring to support different key derivations.
-   Added attributes to exceptions so that you can inspect the data even
    if the signature check failed.


Version 0.13
------------

Released 2012-06-10

-   Small API change that enables customization of the digest module.


Version 0.12
------------

Released 2012-02-22

-   Fixed a problem with the local timezone being used for the epoch
    calculation. This might invalidate some of your signatures if you
    were not running in UTC timezone. You can revert to the old behavior
    by monkey patching ``itsdangerous.EPOCH``.


Version 0.11
------------

Released 2011-07-07

-   Fixed an uncaught value error.


Version 0.10
------------

Released 2011-06-25

-   Refactored interface that the underlying serializers can be swapped
    by passing in a module instead of having to override the payload
    loaders and dumpers. This makes the interface more compatible with
    Django's recent changes.
