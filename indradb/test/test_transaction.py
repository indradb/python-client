import os
import unittest

from indradb import Client, Error, VertexQuery, EdgeQuery, Transaction, EdgeKey, VertexMetadata, EdgeMetadata

class TransactionTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["INDRADB_HOST"]
        self.client = Client(host, scheme="http")

    def r(self, trans):
        return self.client.transaction(trans)

    def test_get_vertices(self):
        [uuid] = self.r(Transaction().create_vertex("foo"))
        [results] = self.r(Transaction().get_vertices(VertexQuery.vertices([uuid])))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, uuid)

    def test_delete_vertices(self):
        [uuid] = self.r(Transaction().create_vertex("foo"))
        [_, results] = self.r(Transaction().delete_vertices(VertexQuery.vertices([uuid])).get_vertices(VertexQuery.vertices([uuid])))
        self.assertEqual(len(results), 0)

    def test_get_edges(self):
        [outbound_id, inbound_id] = self.r(Transaction().create_vertex("foo").create_vertex("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, results] = self.r(Transaction().create_edge(key).get_edges(EdgeQuery.edges([key])))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key.outbound_id, outbound_id)
        self.assertEqual(results[0].key.type, "bar")
        self.assertEqual(results[0].key.inbound_id, inbound_id)

    def test_delete_edges(self):
        [outbound_id, inbound_id] = self.r(Transaction().create_vertex("foo").create_vertex("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, _, count] = self.r(Transaction().create_edge(key).delete_edges(EdgeQuery.edges([key])).get_edge_count(EdgeQuery.edges([key])))
        self.assertEqual(count, 0)

    def test_get_edge_count(self):
        [outbound_id, inbound_id] = self.r(Transaction().create_vertex("foo").create_vertex("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, count] = self.r(Transaction().create_edge(key).get_edge_count(EdgeQuery.edges([key])))
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
        [uuid] = self.r(Transaction().create_vertex("foo"))
        query = VertexQuery.vertices([uuid])

        [first, _, second, _, third] = self.r(Transaction()
            .get_vertex_metadata(query, "foo")
            .set_vertex_metadata(query, "foo", 42)
            .get_vertex_metadata(query, "foo")
            .delete_vertex_metadata(query, "foo")
            .get_vertex_metadata(query, "foo")
        )

        self.assertEqual(len(first), 0)
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0], VertexMetadata(uuid, 42))
        self.assertEqual(len(third), 0)

    def test_edge_metadata(self):
        [outbound_id, inbound_id] = self.r(Transaction().create_vertex("foo").create_vertex("foo"))
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
