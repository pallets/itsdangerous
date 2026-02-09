from __future__ import annotations

import typing as t
import zlib

from ._json import _CompactJSON
from .encoding import base64_decode
from .encoding import base64_encode
from .encoding import want_bytes
from .exc import BadPayload
from .serializer import _PDataSerializer
from .serializer import Serializer
from .timed import TimedSerializer


class URLSafeSerializerMixin(Serializer[str]):
    """Mixed in with a regular serializer it will attempt to zlib
    compress the string to make it shorter if necessary. It will also
    base64 encode the string so that it can safely be placed in a URL.
    """

    default_serializer: _PDataSerializer[str] = _CompactJSON

    def load_payload(
        self,
        payload: bytes,
        *args: t.Any,
        serializer: t.Any | None = None,
        **kwargs: t.Any,
    ) -> t.Any:
        decompress = False

        if payload.startswith(b"."):
            payload = payload[1:]
            decompress = True

        try:
            json = base64_decode(payload)
        except Exception as e:
            raise BadPayload(
                "Could not base64 decode the payload because of an exception",
                original_error=e,
            ) from e

        if decompress:
            try:
                json = zlib.decompress(json)
            except Exception as e:
                raise BadPayload(
                    "Could not zlib decompress the payload before decoding the payload",
                    original_error=e,
                ) from e

        return super().load_payload(json, *args, **kwargs)

    def dump_payload(self, obj: t.Any) -> bytes:
        json = super().dump_payload(obj)
        is_compressed = False
        compressed = zlib.compress(json)

        if len(compressed) < (len(json) - 1):
            json = compressed
            is_compressed = True

        base64d = base64_encode(json)

        if is_compressed:
            base64d = b"." + base64d

        return base64d

    def dumps(self, obj: t.Any, salt: str | bytes | None = None) -> str:
        """Returns a URL-safe, signed string. The payload is always
        base64-encoded, so this method always returns :class:`str`
        regardless of the underlying serializer.
        """
        payload = want_bytes(self.dump_payload(obj))
        rv = self.make_signer(salt).sign(payload)

        if isinstance(rv, bytes):
            return rv.decode("utf-8")

        return rv


class URLSafeSerializer(URLSafeSerializerMixin, Serializer[str]):
    """Works like :class:`.Serializer` but dumps and loads into a URL
    safe string consisting of the upper and lowercase character of the
    alphabet as well as ``'_'``, ``'-'`` and ``'.'``.
    """


class URLSafeTimedSerializer(URLSafeSerializerMixin, TimedSerializer[str]):
    """Works like :class:`.TimedSerializer` but dumps and loads into a
    URL safe string consisting of the upper and lowercase character of
    the alphabet as well as ``'_'``, ``'-'`` and ``'.'``.
    """
