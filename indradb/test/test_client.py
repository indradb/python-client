import os
import unittest

from indradb import Client, VertexQuery, EdgeQuery, EdgeKey

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["INDRADB_HOST"]
        self.client = Client(host, scheme="http")

    def test_script(self):
        result = self.client.script("echo.lua", dict(foo="bar"))
        self.assertEqual(result, dict(foo="bar"))
