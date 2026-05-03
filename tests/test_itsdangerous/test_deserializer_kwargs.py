"""Test for deserializer_kwargs parameter (issue #389)."""
import pytest

from itsdangerous.serializer import Serializer


class CustomSerializer:
    """A custom serializer that requires kwargs for both dumps and loads."""

    def __init__(self):
        self.dumps_kwargs = None
        self.loads_kwargs = None

    def dumps(self, obj, **kwargs):
        self.dumps_kwargs = kwargs
        # Simple serialization: convert to string
        return str(obj)

    def loads(self, payload, **kwargs):
        self.loads_kwargs = kwargs
        # Simple deserialization: convert back to int
        return int(payload)


def test_deserializer_kwargs_basic():
    """Test that deserializer_kwargs are passed to the deserializer."""
    custom_serializer = CustomSerializer()
    serializer = Serializer(
        secret_key="test-key",
        serializer=custom_serializer,
        serializer_kwargs={"dumps_arg": "value1"},
        deserializer_kwargs={"loads_arg": "value2"},
    )

    # Test serialization
    signed = serializer.dumps(42)
    assert custom_serializer.dumps_kwargs == {"dumps_arg": "value1"}

    # Test deserialization
    result = serializer.loads(signed)
    assert result == 42
    assert custom_serializer.loads_kwargs == {"loads_arg": "value2"}


def test_deserializer_kwargs_fallback_to_serializer_kwargs():
    """Test that serializer_kwargs is used when deserializer_kwargs is not provided."""
    custom_serializer = CustomSerializer()
    serializer = Serializer(
        secret_key="test-key",
        serializer=custom_serializer,
        serializer_kwargs={"shared_arg": "value"},
    )

    # Test serialization
    signed = serializer.dumps(42)
    assert custom_serializer.dumps_kwargs == {"shared_arg": "value"}

    # Test deserialization - should use serializer_kwargs
    result = serializer.loads(signed)
    assert result == 42
    assert custom_serializer.loads_kwargs == {"shared_arg": "value"}


def test_deserializer_kwargs_empty_dict():
    """Test that empty deserializer_kwargs overrides serializer_kwargs."""
    custom_serializer = CustomSerializer()
    serializer = Serializer(
        secret_key="test-key",
        serializer=custom_serializer,
        serializer_kwargs={"arg": "value"},
        deserializer_kwargs={},
    )

    # Test serialization
    signed = serializer.dumps(42)
    assert custom_serializer.dumps_kwargs == {"arg": "value"}

    # Test deserialization - should use empty dict
    result = serializer.loads(signed)
    assert result == 42
    assert custom_serializer.loads_kwargs == {}


def test_deserializer_kwargs_with_json():
    """Test that deserializer_kwargs works with json serializer."""
    import json

    class JsonWithKwargs:
        """JSON serializer that tracks kwargs."""

        def __init__(self):
            self.dumps_kwargs = None
            self.loads_kwargs = None

        def dumps(self, obj, **kwargs):
            self.dumps_kwargs = kwargs
            return json.dumps(obj)

        def loads(self, payload, **kwargs):
            self.loads_kwargs = kwargs
            return json.loads(payload)

    custom_json = JsonWithKwargs()
    serializer = Serializer(
        secret_key="test-key",
        serializer=custom_json,
        serializer_kwargs={"indent": 2},
        deserializer_kwargs={"strict": False},
    )

    # Test serialization
    data = {"key": "value"}
    signed = serializer.dumps(data)
    assert custom_json.dumps_kwargs == {"indent": 2}

    # Test deserialization
    result = serializer.loads(signed)
    assert result == data
    assert custom_json.loads_kwargs == {"strict": False}


def test_deserializer_kwargs_backward_compatibility():
    """Test that existing code without deserializer_kwargs still works."""
    # This test ensures backward compatibility
    # Note: serializer_kwargs that are only valid for dumps will cause issues
    # if passed to loads. Users should use deserializer_kwargs to override.
    serializer = Serializer(
        secret_key="test-key",
    )

    # Should work without any issues
    data = {"key": "value"}
    signed = serializer.dumps(data)
    result = serializer.loads(signed)
    assert result == data


def test_deserializer_kwargs_with_incompatible_kwargs():
    """Test that deserializer_kwargs can override incompatible serializer_kwargs."""
    # This test demonstrates the use case where serializer_kwargs and
    # deserializer_kwargs need to be different
    serializer = Serializer(
        secret_key="test-key",
        serializer_kwargs={"indent": 2},  # Only valid for dumps
        deserializer_kwargs={},  # Override to avoid passing indent to loads
    )

    # Should work because deserializer_kwargs overrides serializer_kwargs
    data = {"key": "value"}
    signed = serializer.dumps(data)
    result = serializer.loads(signed)
    assert result == data
