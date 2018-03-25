import os
import uuid
import unittest

from indradb import Client, Error, Vertex, VertexQuery, EdgeQuery, Transaction, EdgeKey, VertexMetadata, EdgeMetadata

class TransactionTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["INDRADB_HOST"]
        self.client = Client(host, scheme="http")

    def r(self, trans):
        return self.client.transaction(trans)

    def test_create_vertex(self):
        id = str(uuid.uuid4())
        vertex = Vertex(id, "foo")
        [_, results] = self.r(Transaction().create_vertex(vertex).get_vertices(VertexQuery.vertices([id])))
        self.assertEqual(len(results), 1)

    def test_get_vertices(self):
        [id] = self.r(Transaction().create_vertex_from_type("foo"))
        [results] = self.r(Transaction().get_vertices(VertexQuery.vertices([id])))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, id)

    def test_delete_vertices(self):
        [id] = self.r(Transaction().create_vertex_from_type("foo"))
        [_, results] = self.r(Transaction().delete_vertices(VertexQuery.vertices([id])).get_vertices(VertexQuery.vertices([id])))
        self.assertEqual(len(results), 0)

    def test_get_edges(self):
        [outbound_id, inbound_id] = self.r(Transaction().create_vertex_from_type("foo").create_vertex_from_type("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, results] = self.r(Transaction().create_edge(key).get_edges(EdgeQuery.edges([key])))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key.outbound_id, outbound_id)
        self.assertEqual(results[0].key.type, "bar")
        self.assertEqual(results[0].key.inbound_id, inbound_id)

    def test_delete_edges(self):
        [outbound_id, inbound_id] = self.r(Transaction().create_vertex_from_type("foo").create_vertex_from_type("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, _, count] = self.r(Transaction().create_edge(key).delete_edges(EdgeQuery.edges([key])).get_edge_count(outbound_id, None, "outbound"))
        self.assertEqual(count, 0)

    def test_get_edge_count(self):
        [outbound_id, inbound_id] = self.r(Transaction().create_vertex_from_type("foo").create_vertex_from_type("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, count] = self.r(Transaction().create_edge(key).get_edge_count(outbound_id, None, "outbound"))
        self.assertEqual(count, 1)

    def test_global_metadata(self):
        [first, _, second, _, third] = self.r(Transaction()
            .get_global_metadata("foo")
            .set_global_metadata("foo", 42)
            .get_global_metadata("foo")
            .delete_global_metadata("foo")
            .get_global_metadata("foo")
        )

        self.assertEqual(first, None)
        self.assertEqual(second, 42)
        self.assertEqual(third, None)

    def test_vertex_metadata(self):
        [id] = self.r(Transaction().create_vertex_from_type("foo"))
        query = VertexQuery.vertices([id])

        [first, _, second, _, third] = self.r(Transaction()
            .get_vertex_metadata(query, "foo")
            .set_vertex_metadata(query, "foo", 42)
            .get_vertex_metadata(query, "foo")
            .delete_vertex_metadata(query, "foo")
            .get_vertex_metadata(query, "foo")
        )

        self.assertEqual(len(first), 0)
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0], VertexMetadata(id, 42))
        self.assertEqual(len(third), 0)

    def test_edge_metadata(self):
        [outbound_id, inbound_id] = self.r(Transaction().create_vertex_from_type("foo").create_vertex_from_type("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        self.r(Transaction().create_edge(key))
        query = EdgeQuery.edges([key])

        [first, _, second, _, third] = self.r(Transaction()
            .get_edge_metadata(query, "foo")
            .set_edge_metadata(query, "foo", 42)
            .get_edge_metadata(query, "foo")
            .delete_edge_metadata(query, "foo")
            .get_edge_metadata(query, "foo")
        )

        self.assertEqual(len(first), 0)
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0], EdgeMetadata(key, 42))
        self.assertEqual(len(third), 0)
