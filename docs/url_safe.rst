.. module:: itsdangerous.url_safe

URL Safe Serialization
======================

Often it is helpful if you can pass these trusted strings in places
where you only have a limited set of characters available. Because of
this, ItsDangerous also provides URL safe serializers:

.. code-block:: python

    from itsdangerous.url_safe import URLSafeSerializer
    s = URLSafeSerializer("secret-key")
    s.dumps([1, 2, 3, 4])
    'WzEsMiwzLDRd.wSPHqC0gR7VUqivlSukJ0IeTDgo'
    s.loads("WzEsMiwzLDRd.wSPHqC0gR7VUqivlSukJ0IeTDgo")
    [1, 2, 3, 4]

.. autoclass:: URLSafeSerializer

.. autoclass:: URLSafeTimedSerializer
