from functools import partial

import pytest

from itsdangerous.url_safe import URLSafeSerializer
from itsdangerous.url_safe import URLSafeTimedSerializer
from test_itsdangerous.test_serializer import TestSerializer
from test_itsdangerous.test_timed import TestTimedSerializer


def test_loads_rejects_unexpected_kwargs():
    serializer = URLSafeSerializer("secret-key")
    signed = serializer.dumps("value")

    with pytest.raises(TypeError, match="unexpected keyword argument 'max_age'"):
        serializer.loads(signed, max_age=-1)


class TestURLSafeSerializer(TestSerializer):
    @pytest.fixture()
    def serializer_factory(self):
        return partial(URLSafeSerializer, secret_key="secret-key")

    @pytest.fixture(params=({"id": 42}, pytest.param("a" * 1000, id="zlib")))
    def value(self, request):
        return request.param


class TestURLSafeTimedSerializer(TestURLSafeSerializer, TestTimedSerializer):
    @pytest.fixture()
    def serializer_factory(self):
        return partial(URLSafeTimedSerializer, secret_key="secret-key")
