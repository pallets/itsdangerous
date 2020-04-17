class BadData(Exception):
    """Raised if bad data of any sort was encountered. This is the base
    for all exceptions that ItsDangerous defines.

    .. versionadded:: 0.15
    """

    message = None

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class BadSignature(BadData):
    """Raised if a signature does not match."""

    def __init__(self, message, payload=None):
        super().__init__(message)

        #: The payload that failed the signature test. In some
        #: situations you might still want to inspect this, even if
        #: you know it was tampered with.
        #:
        #: .. versionadded:: 0.14
        self.payload = payload


class BadTimeSignature(BadSignature):
    """Raised if a time-based signature is invalid. This is a subclass
    of :class:`BadSignature`.
    """

    def __init__(self, message, payload=None, date_signed=None):
        super().__init__(message, payload)

        #: If the signature expired this exposes the date of when the
        #: signature was created. This can be helpful in order to
        #: tell the user how long a link has been gone stale.
        #:
        #: .. versionchanged:: 2.0
        #:     The datetime value is timezone-aware rather than naive.
        #:
        #: .. versionadded:: 0.14
        self.date_signed = date_signed


class SignatureExpired(BadTimeSignature):
    """Raised if a signature timestamp is older than ``max_age``. This
    is a subclass of :exc:`BadTimeSignature`.
    """


class BadHeader(BadSignature):
    """Raised if a signed header is invalid in some form. This only
    happens for serializers that have a header that goes with the
    signature.

    .. versionadded:: 0.24
    """

    def __init__(self, message, payload=None, header=None, original_error=None):
        super().__init__(message, payload)

        #: If the header is actually available but just malformed it
        #: might be stored here.
        self.header = header

        #: If available, the error that indicates why the payload was
        #: not valid. This might be ``None``.
        self.original_error = original_error


class BadPayload(BadData):
    """Raised if a payload is invalid. This could happen if the payload
    is loaded despite an invalid signature, or if there is a mismatch
    between the serializer and deserializer. The original exception
    that occurred during loading is stored on as :attr:`original_error`.

    .. versionadded:: 0.15
    """

    def __init__(self, message, original_error=None):
        super().__init__(message)

        #: If available, the error that indicates why the payload was
        #: not valid. This might be ``None``.
        self.original_error = original_error
