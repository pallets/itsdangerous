from __future__ import annotations

import json as _json
import typing as t


class _CompactJSON:
    """Wrapper around json module that strips whitespace."""

    @staticmethod
    def loads(s: str | bytes) -> t.Any:
        return _json.loads(s)

    @staticmethod
    def dumps(obj: t.Any, *args: t.Any, **kwargs: t.Any) -> str:
        kwargs.setdefault("ensure_ascii", False)
        kwargs.setdefault("separators", (",", ":"))
        return _json.dumps(obj, **kwargs)
