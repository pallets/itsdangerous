:orphan:

.. module:: itsdangerous.jws

JSON Web Signature (JWS)
========================

.. warning::
    .. deprecated:: 2.0
        ItsDangerous will no longer support JWS in version 2.1. Use a
        dedicated JWS/JWT library such as `authlib`_.

.. _authlib: https://authlib.org/

JSON Web Signatures (JWS) work similarly to the existing URL safe
serializer but will emit headers according to `draft-ietf-jose-json-web
-signature <http://self-issued.info/docs/draft-ietf-jose-json-web
-signature.html>`_.

.. code-block:: python

    from itsdangerous import JSONWebSignatureSerializer
    s = JSONWebSignatureSerializer("secret-key")
    s.dumps({"x": 42})
    'eyJhbGciOiJIUzI1NiJ9.eyJ4Ijo0Mn0.ZdTn1YyGz9Yx5B5wNpWRL221G1WpVE5fPCPKNuc6UAo'

When loading the value back the header will not be returned by default
like with the other serializers. However it is possible to also ask for
the header by passing ``return_header=True``. Custom header fields can
be provided upon serialization:

.. code-block:: python

    s.dumps(0, header_fields={"v": 1})
    'eyJhbGciOiJIUzI1NiIsInYiOjF9.MA.wT-RZI9YU06R919VBdAfTLn82_iIQD70J_j-3F4z_aM'
    s.loads(
        "eyJhbGciOiJIUzI1NiIsInYiOjF9"
        ".MA.wT-RZI9YU06R919VBdAfTLn82_iIQD70J_j-3F4z_aM"
    )
    (0, {'alg': 'HS256', 'v': 1})

ItsDangerous only provides HMAC SHA derivatives and the none algorithm
at the moment and does not support the ECC based ones. The algorithm in
the header is checked against the one of the serializer and on a
mismatch a :exc:`~itsdangerous.exc.BadSignature` exception is raised.

.. autoclass:: JSONWebSignatureSerializer
    :members:

.. autoclass:: TimedJSONWebSignatureSerializer
    :members:
