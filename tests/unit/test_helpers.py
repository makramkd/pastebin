import unittest

from pastebin.helpers import format_paste_path, parse_paste_path

class TestHelpers(unittest.TestCase):
    def test_format_paste_path(self):
        shortlink = 'helloworld'
        bucket_name = 'bucket'
        expected = 'shortlink=helloworld,bucket=bucket'
        actual = format_paste_path(shortlink, bucket_name)
        self.assertEqual(expected, actual)

    def test_parse_paste_path(self):
        path = 'shortlink=helloworld,bucket=the_bucket'
        expected = ('helloworld', 'the_bucket')
        actual = parse_paste_path(path)
        self.assertEqual(expected, actual)
