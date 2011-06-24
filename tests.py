import time
import unittest
import itsdangerous as idmod


class SerializerTestCase(unittest.TestCase):
    serializer_class = idmod.Serializer

    def test_dumps_loads(self):
        objects = (['a', 'list'], 'a string', u'a unicode string \u2019',
                   {'a': 'dictionary'}, 42, 42.5)
        s = self.serializer_class('Test')
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
        s = self.serializer_class('Test')
        encoded = s.dumps(value)
        self.assertEqual(value, s.loads(encoded))
        for transform in transforms:
            self.assertRaises(
                idmod.BadSignature, s.loads, transform(encoded))


class TimedSerializerTestCase(SerializerTestCase):
    serializer_class = idmod.TimedSerializer

    def test_decode_with_timeout(self):
        secret_key = 'predictable-key'
        value = u'hello'
        _time = time.time
        time.time = lambda: idmod.EPOCH
        try:
            s = self.serializer_class(secret_key)
            ts = s.dumps(value)
            self.assertNotEqual(ts, idmod.Serializer(secret_key).dumps(value))

            self.assertEqual(s.loads(ts), value)
            time.time = lambda: idmod.EPOCH + 10
            self.assertEqual(s.loads(ts, max_age=11), value)
            self.assertEqual(s.loads(ts, max_age=10), value)
            self.assertRaises(
                idmod.SignatureExpired, s.loads, ts, max_age=9)
        finally:
            time.time = _time



class URLSafeSerializerMixin(object):

    def test_is_base62(self):
        allowed = frozenset('0123456789abcdefghijklmnopqrstuvwxyz' +
                            'ABCDEFGHIJKLMNOPQRSTUVWXYZ_-.')
        objects = (['a', 'list'], 'a string', u'a unicode string \u2019',
                   {'a': 'dictionary'}, 42, 42.5)
        s = self.serializer_class('Test')
        for o in objects:
            value = s.dumps(o)
            self.assert_(set(value).issubset(set(allowed)))
            self.assertNotEqual(o, value)
            self.assertEqual(o, s.loads(value))


class URLSafeSerializerTestCase(URLSafeSerializerMixin, SerializerTestCase):
    serializer_class = idmod.URLSafeSerializer


class URLSafeSerializerTestCase(URLSafeSerializerMixin, SerializerTestCase):
    serializer_class = idmod.URLSafeTimedSerializer


if __name__ == '__main__':
    unittest.main()
