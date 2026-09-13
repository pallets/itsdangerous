from functools import partial

import pytest

from itsdangerous.url_safe import URLSafeSerializer
from itsdangerous.url_safe import URLSafeTimedSerializer
from test_itsdangerous.test_serializer import TestSerializer
from test_itsdangerous.test_timed import TestTimedSerializer


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

class TestURLSafeSerializerMaxAge:
    """Tests for unexpected max_age argument on untimed serializers.

    See https://github.com/pallets/itsdangerous/issues/429
    """

    def test_max_age_raises_typeerror(self):
        """URLSafeSerializer.loads() should raise TypeError for max_age."""
        s = URLSafeSerializer("SECRET")
        signed = s.dumps("value")
        with pytest.raises(TypeError):
            s.loads(signed, max_age=-1)

    def test_max_age_raises_typeerror_none(self):
        """URLSafeSerializer.loads() should raise TypeError even for max_age=None."""
        s = URLSafeSerializer("SECRET")
        signed = s.dumps("value")
        with pytest.raises(TypeError):
            s.loads(signed, max_age=None)

    def test_timed_max_age_still_works(self):
        """URLSafeTimedSerializer.loads() should still accept max_age."""
        s = URLSafeTimedSerializer("SECRET")
        signed = s.dumps("value")
        # Should raise SignatureExpired, not TypeError
        with pytest.raises(Exception) as exc_info:
            s.loads(signed, max_age=-1)
        assert not isinstance(exc_info.value, TypeError)

    def test_no_extra_kwargs(self):
        """URLSafeSerializer.loads() should reject arbitrary kwargs."""
        s = URLSafeSerializer("SECRET")
        signed = s.dumps("value")
        with pytest.raises(TypeError):
            s.loads(signed, unexpected_arg=True)
