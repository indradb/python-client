import os
import uuid
import unittest

from indradb import *

class TransactionTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["INDRADB_HOST"]
        self.client = Client(host)

    def test_create_vertex(self):
        trans = self.client.transaction()
        id = uuid.uuid4()
        v1 = Vertex(id, "foo")
        trans.create_vertex(v1).wait()
        v2 = trans.get_vertices(SpecificVertexQuery(id)).wait()
        self.assertEqual(v2, [v1])

    def test_get_vertices(self):
        trans = self.client.transaction()
        id = trans.create_vertex_from_type("foo").wait()
        results = trans.get_vertices(SpecificVertexQuery(id)).wait()
        self.assertEqual(results, [Vertex(id, "foo")])

    def test_delete_vertices(self):
        trans = self.client.transaction()
        id = trans.create_vertex_from_type("foo").wait()
        trans.delete_vertices(SpecificVertexQuery(id)).wait()
        results = trans.get_vertices(SpecificVertexQuery(id)).wait()
        self.assertEqual(results, [])

    def test_get_edges(self):
        trans = self.client.transaction()
        outbound_id = trans.create_vertex_from_type("foo").wait()
        inbound_id = trans.create_vertex_from_type("foo").wait()
        key = EdgeKey(outbound_id, "bar", inbound_id)
        trans.create_edge(key).wait()
        results = trans.get_edges(SpecificEdgeQuery(key)).wait()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key, key)

    def test_delete_edges(self):
        trans = self.client.transaction()
        outbound_id = trans.create_vertex_from_type("foo").wait()
        inbound_id = trans.create_vertex_from_type("foo").wait()
        key = EdgeKey(outbound_id, "bar", inbound_id)
        trans.create_edge(key).wait()
        trans.delete_edges(SpecificEdgeQuery(key)).wait()
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

    def test_vertex_properties(self):
        trans = self.client.transaction()
        id = trans.create_vertex_from_type("foo").wait()
        query = SpecificVertexQuery(id).property("foo")

        m1 = trans.get_vertex_properties(query).wait()
        trans.set_vertex_properties(query, 42).wait()
        m2 = trans.get_vertex_properties(query).wait()
        trans.delete_vertex_properties(query).wait()
        m3 = trans.get_vertex_properties(query).wait()

        self.assertEqual(m1, [])
        self.assertEqual(m2, [VertexProperty(id, 42)])
        self.assertEqual(m3, [])

    def test_edge_properties(self):
        trans = self.client.transaction()
        outbound_id = trans.create_vertex_from_type("foo").wait()
        inbound_id = trans.create_vertex_from_type("foo").wait()
        key = EdgeKey(outbound_id, "bar", inbound_id)
        trans.create_edge(key).wait()
        query = SpecificEdgeQuery(key).property("foo")

        m1 = trans.get_edge_properties(query).wait()
        trans.set_edge_properties(query, 42).wait()
        m2 = trans.get_edge_properties(query).wait()
        trans.delete_edge_properties(query).wait()
        m3 = trans.get_edge_properties(query).wait()

        self.assertEqual(m1, [])
        self.assertEqual(m2, [EdgeProperty(key, 42)])
        self.assertEqual(m3, [])
