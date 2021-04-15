import json
import typing as _t
from types import ModuleType


class _CompactJSON:
    """Wrapper around json module that strips whitespace."""

    @staticmethod
    def loads(payload: _t.Union[str, bytes]) -> _t.Any:
        return json.loads(payload)

    @staticmethod
    def dumps(obj: _t.Any, **kwargs: _t.Any) -> str:
        kwargs.setdefault("ensure_ascii", False)
        kwargs.setdefault("separators", (",", ":"))
        return json.dumps(obj, **kwargs)


class DeprecatedJSON(ModuleType):
    def __getattribute__(self, item: str) -> _t.Any:
        import warnings

        warnings.warn(
            "Importing 'itsdangerous.json' is deprecated and will be"
            " removed in ItsDangerous 2.1. Use Python's 'json' module"
            " instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(json, item)


deprecated_json = DeprecatedJSON("json")
