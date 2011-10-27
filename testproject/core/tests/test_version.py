from django.test import TestCase

from setman import get_version


__all__ = ('TestVersion', )


VERSIONS = (
    ((0, 1), '0.1'),
    ((0, 1, 'alpha'), '0.1-alpha'),
    ((0, 1, 0), '0.1.0'),
    ((0, 1, None), '0.1'),
)


class TestVersion(TestCase):

    def test_get_version(self):
        for version, result in VERSIONS:
            self.assertEqual(get_version(version), result)
