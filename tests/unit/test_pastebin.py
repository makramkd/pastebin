import asyncio
import unittest
from unittest import mock

from pastebin.api import Pastebin

class TestPastebin(unittest.TestCase):
    def setUp(self):
        self.psql_client = mock.MagicMock()
        self.redis_client = mock.MagicMock()
        self.minio_client = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.pastebin = Pastebin(
            psql_client=self.psql_client,
            redis_client=self.redis_client,
            minio_client=self.minio_client,
            bucket_name='test',
            logger=self.logger,
        )

    def test_create_paste_no_json(self):
        pass

    def test_create_paste_no_contents(self):
        pass

    def test_create_paste_bad_date(self):
        pass

    def test_get_paste_no_shortlink(self):
        pass

    def test_get_paste_expired_shortlink(self):
        pass
