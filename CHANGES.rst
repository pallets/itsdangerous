Version 1.0
-----------

Unreleased

-   Dropped support for Python 2.6 and 3.3.
-   Distribute a universal wheel.
-   Changed default intermediate hash from SHA-1 to SHA-512
-   More compact JSON dumps for unicode strings.
-   Added ``serializer_kwargs`` argument to ``Serializer``.
-   ``base64_decode`` raises ``BadData`` when it is passed invalid data.
-   Added ``media_type`` argument to ``JSONWebSignatureSerializer``.
-   ``ValueError`` is raised when an invalid ``sep`` is passed to ``Signer``.


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
    itsdangerous on Python 2.6.


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
