import time
import pickle
import unittest
from datetime import datetime
import itsdangerous as idmod


class SerializerTestCase(unittest.TestCase):
    serializer_class = idmod.Serializer

    def make_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def test_dumps_loads(self):
        objects = (['a', 'list'], 'a string', u'a unicode string \u2019',
                   {'a': 'dictionary'}, 42, 42.5)
        s = self.make_serializer('Test')
        for o in objects:
            value = s.dumps(o)
            self.assertNotEqual(o, value)
            self.assertEqual(o, s.loads(value))

    def test_decode_detects_tampering(self):
        transforms = (
            lambda s: s.upper(),
            lambda s: s + 'a',
            lambda s: 'a' + s[1:],
            lambda s: s.replace('.', ''),
        )
        value = {
            'foo': 'bar',
            'baz': 1,
        }
        s = self.make_serializer('Test')
        encoded = s.dumps(value)
        self.assertEqual(value, s.loads(encoded))
        for transform in transforms:
            self.assertRaises(
                idmod.BadSignature, s.loads, transform(encoded))

    def test_accepts_unicode(self):
        objects = (['a', 'list'], 'a string', u'a unicode string \u2019',
                   {'a': 'dictionary'}, 42, 42.5)
        s = self.make_serializer('Test')
        for o in objects:
            value = s.dumps(o)
            self.assertNotEqual(o, value)
            self.assertEqual(o, s.loads(unicode(value)))


class TimedSerializerTestCase(SerializerTestCase):
    serializer_class = idmod.TimedSerializer

    def setUp(self):
        self._time = time.time
        time.time = lambda: idmod.EPOCH

    def tearDown(self):
        time.time = self._time        

    def test_decode_with_timeout(self):
        secret_key = 'predictable-key'
        value = u'hello'

        s = self.make_serializer(secret_key)
        ts = s.dumps(value)
        self.assertNotEqual(ts, idmod.Serializer(secret_key).dumps(value))

        self.assertEqual(s.loads(ts), value)
        time.time = lambda: idmod.EPOCH + 10
        self.assertEqual(s.loads(ts, max_age=11), value)
        self.assertEqual(s.loads(ts, max_age=10), value)
        self.assertRaises(
            idmod.SignatureExpired, s.loads, ts, max_age=9)

    def test_decode_return_timestamp(self):
        secret_key = 'predictable-key'
        value = u'hello'

        s = self.make_serializer(secret_key)
        ts = s.dumps(value)
        loaded, timestamp = s.loads(ts, return_timestamp=True)
        self.assertEqual(loaded, value)
        self.assertEqual(timestamp, datetime.utcfromtimestamp(time.time()))


class URLSafeSerializerMixin(object):

    def test_is_base62(self):
        allowed = frozenset('0123456789abcdefghijklmnopqrstuvwxyz' +
                            'ABCDEFGHIJKLMNOPQRSTUVWXYZ_-.')
        objects = (['a', 'list'], 'a string', u'a unicode string \u2019',
                   {'a': 'dictionary'}, 42, 42.5)
        s = self.make_serializer('Test')
        for o in objects:
            value = s.dumps(o)
            self.assert_(set(value).issubset(set(allowed)))
            self.assertNotEqual(o, value)
            self.assertEqual(o, s.loads(value))


class PickleSerializerMixin(object):

    def make_serializer(self, *args, **kwargs):
        kwargs.setdefault('serializer', pickle)
        return super(PickleSerializerMixin, self).make_serializer(*args, **kwargs)


class URLSafeSerializerTestCase(URLSafeSerializerMixin, SerializerTestCase):
    serializer_class = idmod.URLSafeSerializer


class URLSafeTimedSerializerTestCase(URLSafeSerializerMixin, TimedSerializerTestCase):
    serializer_class = idmod.URLSafeTimedSerializer


class PickleSerializerTestCase(PickleSerializerMixin, SerializerTestCase):
    pass


class PickleTimedSerializerTestCase(PickleSerializerMixin, TimedSerializerTestCase):
    pass


class PickleURLSafeSerializerTestCase(PickleSerializerMixin, URLSafeSerializerTestCase):
    pass


class PickleURLSafeTimedSerializerTestCase(PickleSerializerMixin, URLSafeTimedSerializerTestCase):
    pass


if __name__ == '__main__':
    unittest.main()
