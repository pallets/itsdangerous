import json
from types import ModuleType


class _CompactJSON:
    """Wrapper around json module that strips whitespace."""

    @staticmethod
    def loads(payload):
        return json.loads(payload)

    @staticmethod
    def dumps(obj, **kwargs):
        kwargs.setdefault("ensure_ascii", False)
        kwargs.setdefault("separators", (",", ":"))
        return json.dumps(obj, **kwargs)


class DeprecatedJSON(ModuleType):
    def __getattribute__(self, item):
        import warnings

        warnings.warn(
            "Importing 'itsdangerous.json' is deprecated and will be"
            " removed in 2.1. Use Python's 'json' module instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(json, item)


deprecated_json = DeprecatedJSON("json")
