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


BASE62ALPHA = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
EPOCH = time.mktime((2011, 1, 1, 0, 0, 0, 0, 0, 0))


def constant_time_compare(val1, val2):
    """Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.  Do
    not use this function for anything else than comparision with known
    length targets.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in izip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0


class BadSignature(Exception):
    """This error is raised if a signature does not match"""


class SignatureExpired(BadSignature):
    """Signature timestamp is older than required max_age.  This is a
    subclass of :exc:`BadSignature` so you can use the baseclass for
    catching the error.
    """


def base64_encode(string):
    """base64 encodes a single string.  The resulting string is safe for
    putting into URLs.
    """
    return base64.urlsafe_b64encode(string).strip('=')


def base64_decode(string):
    """base64 decodes a single string."""
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


class Signer(object):
    """This class can sign a string and unsign it and validate the
    signature provided.
    """

    def __init__(self, secret_key, salt=None, sep='.'):
        self.secret_key = secret_key
        self.sep = sep
        self.salt = salt or ('%s.%s' %
            (self.__class__.__module__, self.__class__.__name__))

    def get_signature(self, value):
        """Returns the signature for the given value"""
        key = hashlib.sha1(self.salt + 'signer' + self.secret_key).digest()
        mac = hmac.new(key, msg=value, digestmod=hashlib.sha1)
        return base64_encode(mac.digest())

    def sign(self, value):
        """Signs the given string."""
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return '%s%s%s' % (value, self.sep, self.get_signature(value))

    def unsign(self, signed_value):
        """Unsigns the given string."""
        if isinstance(signed_value, unicode):
            value = signed_value.encode('utf-8')
        if self.sep not in signed_value:
            raise BadSignature('No "%s" found in value' % self.sep)
        value, sig = signed_value.rsplit(self.sep, 1)
        if constant_time_compare(sig, self.get_signature(value)):
            return value
        raise BadSignature('Signature "%s" does not match' % sig)

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
        result = Signer.unsign(self, value)
        value, timestamp = result.rsplit(self.sep, 1)
        timestamp = bytes_to_int(base64_decode(timestamp))
        if max_age is not None:
            # Check timestamp is not older than max_age
            age = self.get_timestamp() - timestamp
            if age > max_age:
                raise SignatureExpired(
                    'Signature age %s > %s seconds' % (age, max_age))
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
    """

    def __init__(self, secret_key, salt='itsdangerous'):
        self.secret_key = secret_key
        self.salt = salt

    def load_payload(self, payload):
        """Loads the encoded object.  This implementation uses simplejson."""
        return simplejson.loads(payload)

    def dump_payload(self, obj):
        """Dumps the encoded object into a bytestring.  This implementation
        uses simplejson.
        """
        return simplejson.dumps(obj)

    def make_signer(self):
        """A method that creates a new instance of the signer to be used.
        The default implementation uses the :class:`Signer` baseclass.
        """
        return Signer(self.secret_key, self.salt)

    def dumps(self, obj):
        """Returns URL-safe, sha1 signed base64 compressed JSON string.

        If compress is True (the default) checks if compressing using zlib can
        save some space. Prepends a '.' to signify compression. This is included
        in the signature, to protect against zip bombs.

        Salt can be used to further salt the hash, in case you're worried
        that the NSA might try to brute-force your SHA-1 protected secret.
        """
        return self.make_signer().sign(self.dump_payload(obj))

    def dump(self, obj, f):
        """Like :meth:`dumps` but dumps into a file."""
        f.write(self.dumps(obj))

    def loads(self, s):
        """Reverse of :meth:`dumps`, raises :exc:`BadSignature` if the
        signature validation fails.
        """
        return self.load_payload(self.make_signer().unsign(s))

    def load(self, f):
        """Like :meth:`loads` but loads from a file."""
        return self.loads(f.read())


class TimedSerializer(Serializer):
    """Uses the :class:`TimestampSigner` instead of the default
    :meth:`Signer`.
    """

    def make_signer(self):
        return TimestampSigner(self.secret_key, self.salt)

    def loads(self, s, max_age=None, return_timestamp=False):
        """Reverse of :meth:`dumps`, raises :exc:`BadSignature` if the
        signature validation fails.  If a `max_age` is provided it will
        ensure the signature is not older than that time in seconds.  In
        case the signature is outdated, :exc:`SignatureExpired` is raised
        which is a subclass of :exc:`BadSignature`.  All arguments are
        forwarded to the signer's :meth:`~TimestampSigner.unsign` method.
        """
        base64d = self.make_signer().unsign(s, max_age, return_timestamp)
        return self.load_payload(base64d)


class URLSafeSerializerMixin(object):

    def load_payload(self, payload):
        decompress = False
        if payload[0] == '.':
            payload = payload[1:]
            decompress = True
        json = base64_decode(payload)
        if decompress:
            json = zlib.decompress(json)
        return simplejson.loads(json)

    def dump_payload(self, obj):
        json = simplejson.dumps(obj, separators=(',', ':'))
        is_compressed = False
        compressed = zlib.compress(json)
        if len(compressed) < (len(json) - 1):
            json = compressed
            is_compressed = True
        base64d = base64_encode(json)
        if is_compressed:
            base64d = '.' + base64d
        return base64d


class URLSafeSerializer(URLSafeSerializerMixin, Serializer):
    """Works like :class:`Serializer` but dumps and loads into a URL
    safe string consisting of the upper and lowercase character of the
    alphabet as well as ``'_'``, ``'-'`` and ``'.'``.
    """


class URLSafeTimedSerializer(URLSafeSerializerMixin, TimedSerializer):
    """Works like :class:`TimedSerializer` but dumps and loads into a URL
    safe string consisting of the upper and lowercase character of the
    alphabet as well as ``'_'``, ``'-'`` and ``'.'``.
    """
