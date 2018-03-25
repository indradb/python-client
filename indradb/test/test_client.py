import os
import unittest

from indradb import Client, Transaction, VertexQuery, EdgeQuery, EdgeKey

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["INDRADB_HOST"]
        self.client = Client(host, scheme="http")

    def test_script(self):
        result = self.client.script("echo.lua", dict(foo="bar"))
        self.assertEqual(result, dict(foo="bar"))

    def test_mapreduce(self):
        # Insert at least 1 vertex so we have something to work with. Then
        # grab all the vertices, so we know how many to expect.
        vertices = self.client.transaction(Transaction()
            .create_vertex_from_type("foo")
            .get_vertices(VertexQuery.all())
        )[1]

        # Run a mapreduce script that should, with the argument supplied,
        # yield 2 * the number of certices
        results = list(self.client.mapreduce("count.lua", 2))
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[-1], len(vertices) * 2, results[-1])
