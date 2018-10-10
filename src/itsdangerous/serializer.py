from ._compat import text_type
from ._json import json
from .encoding import want_bytes
from .exc import BadPayload
from .exc import BadSignature
from .signer import Signer


def is_text_serializer(serializer):
    """Checks whether a serializer generates text or binary."""
    return isinstance(serializer.dumps({}), text_type)


class Serializer(object):
    """This class provides a serialization interface on top of the
    signer. It provides a similar API to json/pickle and other modules
    but is structured differently internally. If you want to change the
    underlying implementation for parsing and loading you have to
    override the :meth:`load_payload` and :meth:`dump_payload`
    functions.

    This implementation uses simplejson if available for dumping and
    loading and will fall back to the standard library's json module if
    it's not available.

    You do not need to subclass this class in order to switch out or
    customize the :class:`.Signer`. You can instead pass a different
    class to the constructor as well as keyword arguments as a dict that
    should be forwarded.

    .. code-block:: python3

        s = Serializer(signer_kwargs={'key_derivation': 'hmac'})

    .. versionchanged:: 0.14:
        The ``signer`` and ``signer_kwargs`` parameters were added to
        the constructor.
    """

    #: If a serializer module or class is not passed to the constructor
    #: this one is picked up. This currently defaults to :mod:`json`.
    default_serializer = json

    #: The default :class:`Signer` class that is being used by this
    #: serializer.
    #:
    #: .. versionadded:: 0.14
    default_signer = Signer

    def __init__(
        self,
        secret_key,
        salt=b"itsdangerous",
        serializer=None,
        serializer_kwargs=None,
        signer=None,
        signer_kwargs=None,
    ):
        self.secret_key = want_bytes(secret_key)
        self.salt = want_bytes(salt)
        if serializer is None:
            serializer = self.default_serializer
        self.serializer = serializer
        self.is_text_serializer = is_text_serializer(serializer)
        if signer is None:
            signer = self.default_signer
        self.signer = signer
        self.signer_kwargs = signer_kwargs or {}
        self.serializer_kwargs = serializer_kwargs or {}

    def load_payload(self, payload, serializer=None):
        """Loads the encoded object. This function raises
        :class:`.BadPayload` if the payload is not valid. The
        ``serializer`` parameter can be used to override the serializer
        stored on the class. The encoded ``payload`` should always be
        bytes.
        """
        if serializer is None:
            serializer = self.serializer
            is_text = self.is_text_serializer
        else:
            is_text = is_text_serializer(serializer)
        try:
            if is_text:
                payload = payload.decode("utf-8")
            return serializer.loads(payload)
        except Exception as e:
            raise BadPayload(
                "Could not load the payload because an exception"
                " occurred on unserializing the data.",
                original_error=e,
            )

    def dump_payload(self, obj):
        """Dumps the encoded object. The return value is always bytes.
        If the internal serializer returns text, the value will be
        encoded as UTF-8.
        """
        return want_bytes(self.serializer.dumps(obj, **self.serializer_kwargs))

    def make_signer(self, salt=None):
        """Creates a new instance of the signer to be used. The default
        implementation uses the :class:`.Signer` base class.
        """
        if salt is None:
            salt = self.salt
        return self.signer(self.secret_key, salt=salt, **self.signer_kwargs)

    def dumps(self, obj, salt=None):
        """Returns a signed string serialized with the internal
        serializer. The return value can be either a byte or unicode
        string depending on the format of the internal serializer.
        """
        payload = want_bytes(self.dump_payload(obj))
        rv = self.make_signer(salt).sign(payload)
        if self.is_text_serializer:
            rv = rv.decode("utf-8")
        return rv

    def dump(self, obj, f, salt=None):
        """Like :meth:`dumps` but dumps into a file. The file handle has
        to be compatible with what the internal serializer expects.
        """
        f.write(self.dumps(obj, salt))

    def loads(self, s, salt=None):
        """Reverse of :meth:`dumps`. Raises :exc:`.BadSignature` if the
        signature validation fails.
        """
        s = want_bytes(s)
        return self.load_payload(self.make_signer(salt).unsign(s))

    def load(self, f, salt=None):
        """Like :meth:`loads` but loads from a file."""
        return self.loads(f.read(), salt)

    def loads_unsafe(self, s, salt=None):
        """Like :meth:`loads` but without verifying the signature. This
        is potentially very dangerous to use depending on how your
        serializer works. The return value is ``(signature_valid,
        payload)`` instead of just the payload. The first item will be a
        boolean that indicates if the signature is valid. This function
        never fails.

        Use it for debugging only and if you know that your serializer
        module is not exploitable (for example, do not use it with a
        pickle serializer).

        .. versionadded:: 0.15
        """
        return self._loads_unsafe_impl(s, salt)

    def _loads_unsafe_impl(self, s, salt, load_kwargs=None, load_payload_kwargs=None):
        """Low level helper function to implement :meth:`loads_unsafe`
        in serializer subclasses.
        """
        try:
            return True, self.loads(s, salt=salt, **(load_kwargs or {}))
        except BadSignature as e:
            if e.payload is None:
                return False, None
            try:
                return (
                    False,
                    self.load_payload(e.payload, **(load_payload_kwargs or {})),
                )
            except BadPayload:
                return False, None

    def load_unsafe(self, f, *args, **kwargs):
        """Like :meth:`loads_unsafe` but loads from a file.

        .. versionadded:: 0.15
        """
        return self.loads_unsafe(f.read(), *args, **kwargs)
