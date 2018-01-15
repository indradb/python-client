import os
import unittest

from indradb import Client, VertexQuery, EdgeQuery, Transaction, EdgeKey

class TransactionTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["INDRADB_HOST"]
        account_id = os.environ["INDRADB_ACCOUNT_ID"]
        secret = os.environ["INDRADB_SECRET"]
        self.client = Client(host, account_id, secret, scheme="http")

    def single(self, trans):
        return self.client.transaction(trans)[0]

    def test_get_vertices(self):
        uuid = self.single(Transaction().create_vertex("foo"))
        results = self.single(Transaction().get_vertices(VertexQuery.vertex(uuid)))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, uuid)

    def test_delete_vertices(self):
        uuid = self.single(Transaction().create_vertex("foo"))
        [_, results] = self.client.transaction(Transaction().delete_vertices(VertexQuery.vertex(uuid)).get_vertices(VertexQuery.vertex(uuid)))
        self.assertEqual(len(results), 0)

    def test_get_edges(self):
        [outbound_id, inbound_id] = self.client.transaction(Transaction().create_vertex("foo").create_vertex("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, results] = self.client.transaction(Transaction().create_edge(key, 0.5).get_edges(EdgeQuery.edge(key)))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key.outbound_id, outbound_id)
        self.assertEqual(results[0].key.type, "bar")
        self.assertEqual(results[0].key.inbound_id, inbound_id)
        self.assertEqual(results[0].weight, 0.5)

    def test_get_edge_count(self):
        [outbound_id, inbound_id] = self.client.transaction(Transaction().create_vertex("foo").create_vertex("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, count] = self.client.transaction(Transaction().create_edge(key, 0.5).get_edge_count(EdgeQuery.edge(key)))
        self.assertEqual(count, 1)

    def test_delete_edges(self):
        [outbound_id, inbound_id] = self.client.transaction(Transaction().create_vertex("foo").create_vertex("foo"))
        key = EdgeKey(outbound_id, "bar", inbound_id)
        [_, _, count] = self.client.transaction(Transaction().create_edge(key, 0.5).delete_edges(EdgeQuery.edge(key)).get_edge_count(EdgeQuery.edge(key)))
        self.assertEqual(count, 0)

    def test_run_script(self):
        result = self.single(Transaction().run_script("echo.lua", dict(foo="bar")))
        self.assertEqual(result, dict(foo="bar"))
