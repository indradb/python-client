import os
import uuid
import unittest

from indradb import Client, Vertex, VertexQuery, EdgeQuery, Transaction, EdgeKey, VertexMetadata, EdgeMetadata

class TransactionTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["INDRADB_HOST"]
        self.client = Client(host)

    def test_create_vertex(self):
        trans = self.client.transaction()
        id = uuid.uuid4()
        v1 = Vertex(id, "foo")
        trans.create_vertex(v1).wait()
        v2 = trans.get_vertices(VertexQuery.vertices([id])).wait()
        self.assertEqual(v2, [v1])

    def test_get_vertices(self):
        trans = self.client.transaction()
        id = trans.create_vertex_from_type("foo").wait()
        results = trans.get_vertices(VertexQuery.vertices([id])).wait()
        self.assertEqual(results, [Vertex(id, "foo")])

    def test_delete_vertices(self):
        trans = self.client.transaction()
        id = trans.create_vertex_from_type("foo").wait()
        trans.delete_vertices(VertexQuery.vertices([id])).wait()
        results = trans.get_vertices(VertexQuery.vertices([id])).wait()
        self.assertEqual(results, [])

    def test_get_edges(self):
        trans = self.client.transaction()
        outbound_id = trans.create_vertex_from_type("foo").wait()
        inbound_id = trans.create_vertex_from_type("foo").wait()
        key = EdgeKey(outbound_id, "bar", inbound_id)
        trans.create_edge(key).wait()
        results = trans.get_edges(EdgeQuery.edges([key])).wait()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key, key)

    def test_delete_edges(self):
        trans = self.client.transaction()
        outbound_id = trans.create_vertex_from_type("foo").wait()
        inbound_id = trans.create_vertex_from_type("foo").wait()
        key = EdgeKey(outbound_id, "bar", inbound_id)
        trans.create_edge(key).wait()
        trans.delete_edges(EdgeQuery.edges([key])).wait()
        count = trans.get_edge_count(outbound_id, None, "outbound").wait()
        self.assertEqual(count, 0)

    def test_get_edge_count(self):
        trans = self.client.transaction()
        outbound_id = trans.create_vertex_from_type("foo").wait()
        inbound_id = trans.create_vertex_from_type("foo").wait()
        key = EdgeKey(outbound_id, "bar", inbound_id)
        trans.create_edge(key).wait()
        count = trans.get_edge_count(outbound_id, None, "outbound").wait()
        self.assertEqual(count, 1)

    def test_vertex_metadata(self):
        trans = self.client.transaction()
        id = trans.create_vertex_from_type("foo").wait()
        query = VertexQuery.vertices([id])

        m1 = trans.get_vertex_metadata(query, "foo").wait()
        trans.set_vertex_metadata(query, "foo", 42).wait()
        m2 = trans.get_vertex_metadata(query, "foo").wait()
        trans.delete_vertex_metadata(query, "foo").wait()
        m3 = trans.get_vertex_metadata(query, "foo").wait()

        self.assertEqual(m1, [])
        self.assertEqual(m2, [VertexMetadata(id, 42)])
        self.assertEqual(m3, [])

    def test_edge_metadata(self):
        trans = self.client.transaction()
        outbound_id = trans.create_vertex_from_type("foo").wait()
        inbound_id = trans.create_vertex_from_type("foo").wait()
        key = EdgeKey(outbound_id, "bar", inbound_id)
        trans.create_edge(key).wait()
        query = EdgeQuery.edges([key])

        m1 = trans.get_edge_metadata(query, "foo").wait()
        trans.set_edge_metadata(query, "foo", 42).wait()
        m2 = trans.get_edge_metadata(query, "foo").wait()
        trans.delete_edge_metadata(query, "foo").wait()
        m3 = trans.get_edge_metadata(query, "foo").wait()

        self.assertEqual(m1, [])
        self.assertEqual(m2, [EdgeMetadata(key, 42)])
        self.assertEqual(m3, [])
