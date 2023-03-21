import os
import uuid
import unittest

from indradb import *

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(os.environ["INDRADB_HOST"])

    def test_index_property(self):
        self.client.index_property("foo")

    def test_create_vertex(self):
        id = uuid.uuid4()
        v1 = Vertex(id, "foo")
        self.client.create_vertex(v1)
        v2 = list(self.client.get(SpecificVertexQuery(id)))
        self.assertEqual(v2, [[v1]])

    def test_create_vertex_from_type(self):
        id = self.client.create_vertex_from_type("foo")
        self.assertIsInstance(id, uuid.UUID)

    def test_get_vertices(self):
        id = self.client.create_vertex_from_type("foo")
        results = list(self.client.get(SpecificVertexQuery(id)))
        self.assertEqual(results, [[Vertex(id, "foo")]])

    def test_delete_vertices(self):
        id = self.client.create_vertex_from_type("foo")
        self.client.delete(SpecificVertexQuery(id))
        results = list(self.client.get(SpecificVertexQuery(id)))
        self.assertEqual(results, [[]])

    def test_get_vertex_count(self):
        results = list(self.client.get(AllVertexQuery().count()))
        self.assertGreater(results, [0])

    def test_get_edges(self):
        outbound_id = self.client.create_vertex_from_type("foo")
        inbound_id = self.client.create_vertex_from_type("foo")
        edge = Edge(outbound_id, "bar", inbound_id)
        self.client.create_edge(edge)
        results = list(self.client.get(SpecificEdgeQuery(edge)))
        self.assertEqual(results, [[edge]])

    def test_delete_edges(self):
        outbound_id = self.client.create_vertex_from_type("foo")
        inbound_id = self.client.create_vertex_from_type("foo")
        edge = Edge(outbound_id, "bar", inbound_id)
        self.client.create_edge(edge)
        self.client.delete(SpecificEdgeQuery(edge))
        count = list(self.client.get(SpecificVertexQuery(outbound_id).outbound()))
        self.assertEqual(count, [[]])

    def test_get_edge_count(self):
        outbound_id = self.client.create_vertex_from_type("foo")
        inbound_id = self.client.create_vertex_from_type("foo")
        edge = Edge(outbound_id, "bar", inbound_id)
        self.client.create_edge(edge)
        count = list(self.client.get(SpecificVertexQuery(outbound_id).outbound()))
        self.assertEqual(count, [[edge]])

    def test_vertex_properties(self):
        id = self.client.create_vertex_from_type("foo")
        query = SpecificVertexQuery(id)

        m1 = list(self.client.get(query.properties().name("foo")))
        self.client.set_properties(query, "foo", 42)
        m2 = list(self.client.get(query.properties().name("foo")))
        self.client.delete(query)
        m3 = list(self.client.get(query.properties().name("foo")))

        self.assertEqual(m1, [[]])
        self.assertEqual(m2, [[VertexProperties(Vertex(id, "foo"), [NamedProperty("foo", 42)])]])
        self.assertEqual(m3, [[]])

    def test_edge_properties(self):
        outbound_id = self.client.create_vertex_from_type("foo")
        inbound_id = self.client.create_vertex_from_type("foo")
        edge = Edge(outbound_id, "bar", inbound_id)
        self.client.create_edge(edge)
        query = SpecificEdgeQuery(edge)

        m1 = list(self.client.get(query.properties().name("foo")))
        self.client.set_properties(query, "foo", 42)
        m2 = list(self.client.get(query.properties().name("foo")))
        self.client.delete(query.properties())
        m3 = list(self.client.get(query.properties().name("foo")))

        self.assertEqual(m1, [[]])
        self.assertEqual(m2, [[EdgeProperties(edge, [NamedProperty("foo", 42)])]])
        self.assertEqual(m3, [[]])

    def test_get_all_vertex_properties(self):
        id = self.client.create_vertex_from_type("foo")
        query = SpecificVertexQuery(id)

        m1 = list(self.client.get(query.properties()))
        self.client.set_properties(query, "foo", 42)
        m2 = list(self.client.get(query.properties()))
        self.client.delete(query.properties().name("foo"))
        m3 = list(self.client.get(query.properties()))

        self.assertEqual(m1, [[]])
        self.assertEqual(m2, [[VertexProperties(Vertex(id, "foo"), [NamedProperty("foo", 42)])]])
        self.assertEqual(m3, [[]])

    def test_get_all_edge_properties(self):
        outbound_id = self.client.create_vertex_from_type("foo")
        inbound_id = self.client.create_vertex_from_type("foo")
        edge = Edge(outbound_id, "bar", inbound_id)
        self.client.create_edge(edge)
        query = SpecificEdgeQuery(edge)

        m1 = list(self.client.get(query.properties()))
        self.client.set_properties(query, "foo", 42)
        m2 = list(self.client.get(query.properties()))
        self.client.delete(query.properties().name("foo"))
        m3 = list(self.client.get(query.properties()))

        self.assertEqual(m1, [[]])
        self.assertEqual(m2, [[EdgeProperties(edge, [NamedProperty("foo", 42)])]])
        self.assertEqual(m3, [[]])

class BulkInserterTestCase(unittest.TestCase):
    def test_bulk_insert(self):
        client = Client(os.environ["INDRADB_HOST"])

        v1 = Vertex(uuid.uuid1(), "foo")
        v2 = Vertex(uuid.uuid1(), "foo")
        edge = Edge(v1.id, "bar", v2.id)

        # insert everything
        inserter = BulkInserter()
        inserter.vertex(v1)
        inserter.vertex(v2)
        inserter.edge(edge)
        inserter.vertex_property(v1.id, "baz", True)
        inserter.edge_property(edge, "bez", False)
        inserter.execute(client)

        # ensure vertices exist
        results = list(client.get(SpecificVertexQuery(v1.id)))
        self.assertEqual(results, [[v1]])
        results = list(client.get(SpecificVertexQuery(v2.id)))
        self.assertEqual(results, [[v2]])

        # ensure the edge exists
        results = list(client.get(SpecificEdgeQuery(edge)))
        self.assertEqual(results, [[edge]])

        # ensure the vertex property exists
        query = SpecificVertexQuery(v1.id).properties().name("baz")
        results = list(client.get(query))
        self.assertEqual(results, [[VertexProperties(v1, [NamedProperty("baz", True)])]])

        # ensure the edge property exists
        query = SpecificEdgeQuery(edge).properties().name("bez")
        results = list(client.get(query))
        self.assertEqual(results, [[EdgeProperties(edge, [NamedProperty("bez", False)])]])
