import os
import unittest

from indradb import Client, VertexQuery, EdgeQuery, EdgeKey

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["INDRADB_HOST"]
        self.client = Client(host, scheme="http")

    def test_get_vertices(self):
        uuid = self.client.create_vertex("foo")
        results = self.client.get_vertices(VertexQuery.vertices([uuid]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, uuid)

    def test_delete_vertices(self):
        uuid = self.client.create_vertex("foo")
        self.client.delete_vertices(VertexQuery.vertices([uuid]))
        results = self.client.get_vertices(VertexQuery.vertices([uuid]))
        self.assertEqual(len(results), 0)

    def test_get_edges(self):
        outbound_id = self.client.create_vertex("foo")
        inbound_id = self.client.create_vertex("foo")
        key = EdgeKey(outbound_id, "bar", inbound_id)
        self.client.create_edge(key, 0.5)
        results = self.client.get_edges(EdgeQuery.edges([key]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key.outbound_id, outbound_id)
        self.assertEqual(results[0].key.type, "bar")
        self.assertEqual(results[0].key.inbound_id, inbound_id)

    def test_get_edge_count(self):
        outbound_id = self.client.create_vertex("foo")
        inbound_id = self.client.create_vertex("foo")
        key = EdgeKey(outbound_id, "bar", inbound_id)
        self.client.create_edge(key, 0.5)
        count = self.client.get_edge_count(EdgeQuery.edges([key]))
        self.assertEqual(count, 1)

    def test_delete_edges(self):
        outbound_id = self.client.create_vertex("foo")
        inbound_id = self.client.create_vertex("foo")
        key = EdgeKey(outbound_id, "bar", inbound_id)
        self.client.create_edge(key, 0.5)
        self.client.delete_edges(EdgeQuery.edges([key]))
        count = self.client.get_edge_count(EdgeQuery.edges([key]))
        self.assertEqual(count, 0)

    def test_script(self):
        result = self.client.script("echo.lua", dict(foo="bar"))
        self.assertEqual(result, dict(foo="bar"))
