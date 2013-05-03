# -*- coding: utf-8 -*-
"""
    itsdangerous
    ~~~~~~~~~~~~

    A module that implements various functions to deal with untrusted
    sources.  Mainly useful for web applications.

    :copyright: (c) 2011 by Armin Ronacher and the Django Software Foundation.
    :license: BSD, see LICENSE for more details.
"""
import base64
import hashlib
import hmac
import zlib
import time
from itertools import izip, imap
from datetime import datetime


try:
    import simplejson
except ImportError:
    try:
        from django.utils import simplejson
    except ImportError:
        import json as simplejson


# 2011/01/01 in UTC
EPOCH = 1293840000


def constant_time_compare(val1, val2):
    """Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.  Do
    not use this function for anything else than comparision with known
    length targets.

    This is should be implemented in C in order to get it completely right.
    """
    len_eq = len(val1) == len(val2)
    if len_eq:
        result = 0
        left = val1
    else:
        result = 1
        left = val2
    for x, y in izip(left, val2):
        result |= ord(x) ^ ord(y)
    return result == 0


class BadData(Exception):
    """Raised if bad data of any sort was encountered.  This is the
    base for all exceptions that itsdangerous is currently using.

    .. versionadded:: 0.15
    """
    message = None

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.message.decode('utf-8')


class BadPayload(BadData):
    """This error is raised in situations when payload is loaded without
    checking the signature first and an exception happend as a result of
    that.  The original exception that caused that will be stored on the
    exception as :attr:`original_error`.

    .. versionadded:: 0.15
    """

    def __init__(self, message, original_error=None):
        BadData.__init__(self, message)
        #: If available, the error that indicates why the payload
        #: was not valid.  This might be `None`.
        self.original_error = original_error


class BadSignature(BadData):
    """This error is raised if a signature does not match.  As of
    itsdangerous 0.14 there are helpful attributes on the exception
    instances.  You can also catch down the baseclass :exc:`BadData`.
    """

    def __init__(self, message, payload=None):
        BadData.__init__(self, message)
        #: The payload that failed the signature test.  In some
        #: situations you might still want to inspect this, even if
        #: you know it was tampered with.
        #:
        #: .. versionadded:: 0.14
        self.payload = payload


class BadTimeSignature(BadSignature):
    """Raised for time based signatures that fail.  This is a subclass
    of :class:`BadSignature` so you can catch those down as well.
    """

    def __init__(self, message, payload=None, date_signed=None):
        BadSignature.__init__(self, message, payload)

        #: If the signature expired this exposes the date of when the
        #: signature was created.  This can be helpful in order to
        #: tell the user how long a link has been gone stale.
        #:
        #: .. versionadded:: 0.14
        self.date_signed = date_signed


class SignatureExpired(BadTimeSignature):
    """Signature timestamp is older than required max_age.  This is a
    subclass of :exc:`BadTimeSignature` so you can use the baseclass for
    catching the error.
    """


def base64_encode(string):
    """base64 encodes a single string.  The resulting string is safe for
    putting into URLs.
    """
    return base64.urlsafe_b64encode(string).strip('=')


def base64_decode(string):
    """base64 decodes a single string."""
    if isinstance(string, unicode):
        string = string.encode('ascii', 'ignore')
    return base64.urlsafe_b64decode(string + '=' * (-len(string) % 4))


def int_to_bytes(num):
    assert num >= 0
    rv = []
    while num:
        rv.append(chr(num & 0xff))
        num >>= 8
    return ''.join(reversed(rv))


def bytes_to_int(bytes):
    return reduce(lambda a, b: a << 8 | b, imap(ord, bytes), 0)


class SigningAlgorithm(object):
    """Subclasses of `SigningAlgorithm` have to implement `get_signature` to
    provide signature generation functionality.
    """

    def get_signature(self, key, value):
        """Returns the signature for the given key and value"""
        raise NotImplementedError()


class NoneAlgorithm(SigningAlgorithm):
    """This class provides a algorithm that does not perform any signing and
    returns an empty signature.
    """

    def get_signature(self, key, value):
        return ''


class HMACAlgorithm(SigningAlgorithm):
    """This class provides signature generation using HMACs."""

    #: The digest method to use with the MAC algorithm.  This defaults to sha1
    #: but can be changed for any other function in the hashlib module.
    default_digest_method = staticmethod(hashlib.sha1)

    def __init__(self, digest_method=None):
        if digest_method is None:
            digest_method = self.default_digest_method
        self.digest_method = digest_method

    def get_signature(self, key, value):
        mac = hmac.new(key, msg=value, digestmod=self.digest_method)
        return mac.digest()


class Signer(object):
    """This class can sign a string and unsign it and validate the
    signature provided.

    Salt can be used to namespace the hash, so that a signed string is only
    valid for a given namespace.  Leaving this at the default value or re-using
    a salt value across different parts of your application where the same
    signed value in one part can mean something different in another part
    is a security risk.

    See :ref:`the-salt` for an example of what the salt is doing and how you
    can utilize it.

    .. versionadded:: 0.14
       `key_derivation` and `digest_method` were added as arguments to the
       class constructor.

    .. versionadded:: 0.18
        `algorithm` was added as an argument to the class constructor.
    """

    #: The digest method to use for the signer.  This defaults to sha1 but can
    #: be changed for any other function in the hashlib module.
    #:
    #: .. versionchanged:: 0.14
    default_digest_method = staticmethod(hashlib.sha1)

    #: Controls how the key is derived.  The default is Django style
    #: concatenation.  Possible values are ``concat``, ``django-concat``
    #: and ``hmac``.  This is used for deriving a key from the secret key
    #: with an added salt.
    #:
    #: .. versionadded:: 0.14
    default_key_derivation = 'django-concat'

    def __init__(self, secret_key, salt=None, sep='.', key_derivation=None,
                 digest_method=None, algorithm=None):
        self.secret_key = secret_key
        self.sep = sep
        self.salt = salt or 'itsdangerous.Signer'
        if key_derivation is None:
            key_derivation = self.default_key_derivation
        self.key_derivation = key_derivation
        if digest_method is None:
            digest_method = self.default_digest_method
        self.digest_method = digest_method
        if algorithm is None:
            algorithm = HMACAlgorithm(self.digest_method)
        self.algorithm = algorithm

    def derive_key(self):
        """This method is called to derive the key.  If you're unhappy with
        the default key derivation choices you can override them here.
        Keep in mind that the key derivation in itsdangerous is not intended
        to be used as a security method to make a complex key out of a short
        password.  Instead you should use large random secret keys.
        """
        if self.key_derivation == 'concat':
            return self.digest_method(self.salt + self.secret_key).digest()
        elif self.key_derivation == 'django-concat':
            return self.digest_method(self.salt + 'signer' +
                self.secret_key).digest()
        elif self.key_derivation == 'hmac':
            mac = hmac.new(self.secret_key, digestmod=self.digest_method)
            mac.update(self.salt)
            return mac.digest()
        elif self.key_derivation == 'none':
            return self.secret_key
        else:
            raise TypeError('Unknown key derivation method')

    def get_signature(self, value):
        """Returns the signature for the given value"""
        key = self.derive_key()
        sig = self.algorithm.get_signature(key, value)
        return base64_encode(sig)

    def sign(self, value):
        """Signs the given string."""
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return '%s%s%s' % (value, self.sep, self.get_signature(value))

    def unsign(self, signed_value):
        """Unsigns the given string."""
        if isinstance(signed_value, unicode):
            signed_value = signed_value.encode('utf-8')
        if self.sep not in signed_value:
            raise BadSignature('No "%s" found in value' % self.sep)
        value, sig = signed_value.rsplit(self.sep, 1)
        if constant_time_compare(sig, self.get_signature(value)):
            return value
        raise BadSignature('Signature "%s" does not match' % sig,
                           payload=value)

    def validate(self, signed_value):
        """Just validates the given signed value.  Returns `True` if the
        signature exists and is valid, `False` otherwise."""
        try:
            self.unsign(signed_value)
            return True
        except BadSignature:
            return False


class TimestampSigner(Signer):
    """Works like the regular :class:`Signer` but also records the time
    of the signing and can be used to expire signatures.  The unsign
    method can rause a :exc:`SignatureExpired` method if the unsigning
    failed because the signature is expired.  This exception is a subclass
    of :exc:`BadSignature`.
    """

    def get_timestamp(self):
        """Returns the current timestamp.  This implementation returns the
        seconds since 1/1/2011.  The function must return an integer.
        """
        return int(time.time() - EPOCH)

    def timestamp_to_datetime(self, ts):
        """Used to convert the timestamp from `get_timestamp` into a
        datetime object.
        """
        return datetime.utcfromtimestamp(ts + EPOCH)

    def sign(self, value):
        """Signs the given string and also attaches a time information."""
        timestamp = base64_encode(int_to_bytes(self.get_timestamp()))
        value = '%s%s%s' % (value, self.sep, timestamp)
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return '%s%s%s' % (value, self.sep, self.get_signature(value))

    def unsign(self, value, max_age=None, return_timestamp=False):
        """Works like the regular :meth:`~Signer.unsign` but can also
        validate the time.  See the base docstring of the class for
        the general behavior.  If `return_timestamp` is set to `True`
        the timestamp of the signature will be returned as naive
        :class:`datetime.datetime` object in UTC.
        """
        try:
            result = Signer.unsign(self, value)
            sig_error = None
        except BadSignature, e:
            sig_error = e
            result = e.payload or ''

        # If there is no timestamp in the result there is something
        # seriously wrong.  In case there was a signature error, we raise
        # that one directly, otherwise we have a weird situation in which
        # we shouldn't have come except someone uses a time-based serializer
        # on non-timestamp data, so catch that.
        if not self.sep in result:
            if sig_error:
                raise sig_error
            raise BadTimeSignature('timestamp missing', payload=result)

        value, timestamp = result.rsplit(self.sep, 1)
        try:
            timestamp = bytes_to_int(base64_decode(timestamp))
        except Exception:
            timestamp = None

        # Signature is *not* okay.  Raise a proper error now that we have
        # split the value and the timestamp.
        if sig_error is not None:
            raise BadTimeSignature(unicode(sig_error), payload=value,
                                   date_signed=timestamp)

        # Signature was okay but the timestamp is actually not there or
        # malformed.  Should not happen, but well.  We handle it nonetheless
        if timestamp is None:
            raise BadTimeSignature(u'Malformed timestamp', payload=value)

        # Check timestamp is not older than max_age
        if max_age is not None:
            age = self.get_timestamp() - timestamp
            if age > max_age:
                raise SignatureExpired(
                    'Signature age %s > %s seconds' % (age, max_age),
                    payload=value,
                    date_signed=self.timestamp_to_datetime(timestamp))

        if return_timestamp:
            return value, self.timestamp_to_datetime(timestamp)
        return value

    def validate(self, signed_value, max_age=None):
        """Just validates the given signed value.  Returns `True` if the
        signature exists and is valid, `False` otherwise."""
        try:
            self.unsign(signed_value, max_age=max_age)
            return True
        except BadSignature:
            return False


class Serializer(object):
    """This class provides a serialization interface on top of the
    signer.  It provides a similar API to json/pickle/simplejson and
    other modules but is slightly differently structured internally.
    If you want to change the underlying implementation for parsing and
    loading you have to override the :meth:`load_payload` and
    :meth:`dump_payload` functions.

    This implementation uses simplejson for dumping and loading.

    Starting with 0.14 you do not need to subclass this class in order
    to switch out or customer the :class:`Signer`.  You can instead
    also pass a different class to the constructor as well as
    keyword arguments as dictionary that should be forwarded::

        s = Serializer(signer_kwargs={'key_derivation': 'hmac'})

    .. versionchanged:: 0.14:
       The `signer` and `signer_kwargs` parameters were added to the
       constructor.
    """

    #: If a serializer module or class is not passed to the constructor
    #: this one is picked up.  This currently defaults to :mod:`json`.
    default_serializer = simplejson

    #: The default :class:`Signer` class that is being used by this
    #: serializer.
    #:
    #: .. versionadded:: 0.14
    default_signer = Signer

    def __init__(self, secret_key, salt='itsdangerous', serializer=None,
                 signer=None, signer_kwargs=None):
        self.secret_key = secret_key
        self.salt = salt
        if serializer is None:
            serializer = self.default_serializer
        self.serializer = serializer
        if signer is None:
            signer = self.default_signer
        self.signer = signer
        self.signer_kwargs = signer_kwargs or {}

    def load_payload(self, payload, serializer=None):
        """Loads the encoded object.  This implementation uses simplejson.
        This function raises :class:`BadPayload` if the payload is not
        valid.  The `serializer` parameter can be used to override the
        serializer stored on the class.
        """
        if serializer is None:
            serializer = self.serializer
        try:
            if isinstance(payload, unicode):
                payload = payload.encode('utf-8')
            return serializer.loads(payload)
        except Exception, e:
            raise BadPayload(u'Could not load the payload because an '
                u'exception ocurred on unserializing the data',
                original_error=e)

    def dump_payload(self, obj):
        """Dumps the encoded object into a bytestring.  This implementation
        uses simplejson.
        """
        return self.serializer.dumps(obj)

    def make_signer(self, salt=None):
        """A method that creates a new instance of the signer to be used.
        The default implementation uses the :class:`Signer` baseclass.
        """
        if salt is None:
            salt = self.salt
        return self.signer(self.secret_key, salt=salt, **self.signer_kwargs)

    def dumps(self, obj, salt=None):
        """Returns URL-safe, signed base64 compressed JSON string.

        If compress is True (the default) checks if compressing using zlib can
        save some space. Prepends a '.' to signify compression. This is included
        in the signature, to protect against zip bombs.
        """
        return self.make_signer(salt).sign(self.dump_payload(obj))

    def dump(self, obj, f, salt=None):
        """Like :meth:`dumps` but dumps into a file."""
        f.write(self.dumps(obj, salt))

    def loads(self, s, salt=None):
        """Reverse of :meth:`dumps`, raises :exc:`BadSignature` if the
        signature validation fails.
        """
        return self.load_payload(self.make_signer(salt).unsign(s))

    def load(self, f, salt=None):
        """Like :meth:`loads` but loads from a file."""
        return self.loads(f.read(), salt)

    def loads_unsafe(self, s, salt=None):
        """Like :meth:`loads` but without verifying the signature.  This is
        potentially very dangerous to use depending on how your serializer
        works.  The return value is ``(signature_okay, payload)`` instead of
        just the payload.  The first item will be a boolean that indicates
        if the signature is okay (``True``) or if it failed.  This function
        never fails.

        Use it for debugging only and if you know that your serializer module
        is not exploitable (eg: do not use it with a pickle serializer).

        .. versionadded:: 0.15
        """
        return self._loads_unsafe_impl(s, salt)

    def _loads_unsafe_impl(self, s, salt, load_kwargs=None,
                           load_payload_kwargs=None):
        """Lowlevel helper function to implement :meth:`loads_unsafe` in
        serializer subclasses.
        """
        try:
            return True, self.loads(s, salt=salt, **(load_kwargs or {}))
        except BadSignature, e:
            if e.payload is None:
                return False, None
            try:
                return False, self.load_payload(e.payload,
                    **(load_payload_kwargs or {}))
            except BadPayload:
                return False, None

    def load_unsafe(self, f, *args, **kwargs):
        """Like :meth:`loads_unsafe` but loads from a file.

        .. versionadded:: 0.15
        """
        return self.loads_unsafe(f.read(), *args, **kwargs)


class TimedSerializer(Serializer):
    """Uses the :class:`TimestampSigner` instead of the default
    :meth:`Signer`.
    """

    default_signer = TimestampSigner

    def loads(self, s, max_age=None, return_timestamp=False, salt=None):
        """Reverse of :meth:`dumps`, raises :exc:`BadSignature` if the
        signature validation fails.  If a `max_age` is provided it will
        ensure the signature is not older than that time in seconds.  In
        case the signature is outdated, :exc:`SignatureExpired` is raised
        which is a subclass of :exc:`BadSignature`.  All arguments are
        forwarded to the signer's :meth:`~TimestampSigner.unsign` method.
        """
        base64d, timestamp = self.make_signer(salt) \
            .unsign(s, max_age, return_timestamp=True)
        payload = self.load_payload(base64d)
        if return_timestamp:
            return payload, timestamp
        return payload

    def loads_unsafe(self, s, max_age=None, salt=None):
        load_kwargs = {'max_age': max_age}
        load_payload_kwargs = {}
        return self._loads_unsafe_impl(s, salt, load_kwargs, load_payload_kwargs)


class JSONWebSignatureSerializer(Serializer):
    """This serializer implements JSON Web Signature (JWS) support.  Only
    supports the JWS Compact Serialization.
    """

    jws_algorithms = {
        'HS256': HMACAlgorithm(hashlib.sha256),
        'HS384': HMACAlgorithm(hashlib.sha384),
        'HS512': HMACAlgorithm(hashlib.sha512),
        'none': NoneAlgorithm(),
    }

    #: The default algorithm to use for signature generation
    default_algorithm = 'HS256'

    def __init__(self, secret_key, salt=None, signer_kwargs=None, algorithm_name=None):
        self.secret_key = secret_key
        self.salt = salt
        self.serializer = compact_json
        self.signer = Signer
        self.signer_kwargs = signer_kwargs or {}
        if algorithm_name is None:
            algorithm_name = self.default_algorithm
        self.algorithm_name = algorithm_name
        self.algorithm = self.make_algorithm(algorithm_name)

    def load_payload(self, payload, return_header=False):
        if '.' not in payload:
            raise BadPayload('No "." found in value')
        base64d_header, base64d_payload = payload.split('.', 1)
        try:
            json_header = base64_decode(base64d_header)
            json_payload = base64_decode(base64d_payload)
        except Exception, e:
            raise BadPayload(u'Could not base64 decode the payload because of '
                u'an exception', original_error=e)
        header = Serializer.load_payload(self, json_header,
            serializer=simplejson)
        if not isinstance(header, dict):
            raise BadPayload(u'Header payload is not a JSON object')
        payload = Serializer.load_payload(self, json_payload)
        if return_header:
            return payload, header
        return payload

    def dump_payload(self, header, obj):
        base64d_header = base64_encode(self.serializer.dumps(header))
        base64d_payload = base64_encode(self.serializer.dumps(obj))
        return '%s.%s' % (base64d_header, base64d_payload)

    def make_algorithm(self, algorithm_name):
        try:
            return self.jws_algorithms[algorithm_name]
        except KeyError:
            raise NotImplementedError("Algorithm not supported")

    def make_signer(self, salt=None, algorithm=None):
        if salt is None:
            salt is self.salt
        key_derivation = 'none' if salt is None else None
        if algorithm is None:
            algorithm = self.algorithm
        return self.signer(self.secret_key, salt=salt, sep='.',
            key_derivation=key_derivation, algorithm=algorithm)

    def make_header(self, header_fields):
        header = header_fields.copy() if header_fields else {}
        header['alg'] = self.algorithm_name
        return header

    def dumps(self, obj, salt=None, header_fields=None):
        """Like :meth:`~Serializer.dumps` but creates a JSON Web Signature.  It
        also allows for specifying additional fields to be included in the JWS
        Header.
        """
        header = self.make_header(header_fields)
        signer = self.make_signer(salt, self.algorithm)
        return signer.sign(self.dump_payload(header, obj))

    def loads(self, s, salt=None, return_header=False):
        """Reverse of :meth:`dumps`. If requested via `return_header` it will
        return a tuple of payload and header.
        """
        payload, header = self.load_payload(
            self.make_signer(salt, self.algorithm).unsign(s),
            return_header=True)
        if header.get('alg') != self.algorithm_name:
            raise BadSignature('Algorithm mismatch')
        if return_header:
            return payload, header
        return payload

    def loads_unsafe(self, s, salt=None, return_header=False):
        kwargs = {'return_header': return_header}
        return self._loads_unsafe_impl(s, salt, kwargs, kwargs)


class URLSafeSerializerMixin(object):
    """Mixed in with a regular serializer it will attempt to zlib compress
    the string to make it shorter if necessary.  It will also base64 encode
    the string so that it can safely be placed in a URL.
    """

    def load_payload(self, payload):
        decompress = False
        if payload[0] == '.':
            payload = payload[1:]
            decompress = True
        try:
            json = base64_decode(payload)
        except Exception, e:
            raise BadPayload(u'Could not base64 decode the payload because of '
                u'an exception', original_error=e)
        if decompress:
            try:
                json = zlib.decompress(json)
            except Exception, e:
                raise BadPayload(u'Could not zlib decompress the payload before '
                    u'decoding the payload', original_error=e)
        return super(URLSafeSerializerMixin, self).load_payload(json)

    def dump_payload(self, obj):
        json = super(URLSafeSerializerMixin, self).dump_payload(obj)
        is_compressed = False
        compressed = zlib.compress(json)
        if len(compressed) < (len(json) - 1):
            json = compressed
            is_compressed = True
        base64d = base64_encode(json)
        if is_compressed:
            base64d = '.' + base64d
        return base64d


class _CompactJSON(object):
    """Wrapper around simplejson that strips whitespace.
    """

    def loads(self, payload):
        return simplejson.loads(payload)

    def dumps(self, obj):
        return simplejson.dumps(obj, separators=(',', ':'))


compact_json = _CompactJSON()


class URLSafeSerializer(URLSafeSerializerMixin, Serializer):
    """Works like :class:`Serializer` but dumps and loads into a URL
    safe string consisting of the upper and lowercase character of the
    alphabet as well as ``'_'``, ``'-'`` and ``'.'``.
    """
    default_serializer = compact_json


class URLSafeTimedSerializer(URLSafeSerializerMixin, TimedSerializer):
    """Works like :class:`TimedSerializer` but dumps and loads into a URL
    safe string consisting of the upper and lowercase character of the
    alphabet as well as ``'_'``, ``'-'`` and ``'.'``.
    """
    default_serializer = compact_json
