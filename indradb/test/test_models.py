import os
import unittest
import arrow

from indradb import Vertex, EdgeKey, Edge, VertexQuery, EdgeQuery

FIXED_DATETIME = arrow.get("2017-04-10T23:20:00+00.00")

class VertexTestCase(unittest.TestCase):
    def test_to_dict(self):
        vertex = Vertex(3, "foo")
        self.assertEqual(vertex.to_dict(), dict(id=3, type="foo"))

    def test_from_dict(self):
        d = dict(id=3, type="foo")
        self.assertEqual(Vertex.from_dict(d), Vertex(3, "foo"))

class EdgeKeyTestCase(unittest.TestCase):
    def test_to_dict(self):
        key = EdgeKey(3, "foo", 4)
        self.assertEqual(key.to_dict(), dict(outbound_id=3, type="foo", inbound_id=4))

    def test_from_dict(self):
        d = dict(outbound_id=3, type="foo", inbound_id=4)
        self.assertEqual(EdgeKey.from_dict(d), EdgeKey(3, "foo", 4))

class EdgeTestCase(unittest.TestCase):
    def test_to_dict(self):
        edge = Edge(EdgeKey(3, "foo", 4), 0.5, FIXED_DATETIME)
        self.assertEqual(edge.to_dict(), dict(
            key=dict(outbound_id=3, type="foo", inbound_id=4),
            weight=0.5,
            created_datetime="2017-04-10T23:20:00+00:00",
        ))

    def test_from_dict(self):
        d = dict(
            key=dict(outbound_id=3, type="foo", inbound_id=4),
            weight=0.5,
            created_datetime="2017-04-10T23:20:00",
        )
        self.assertEqual(Edge.from_dict(d), Edge(EdgeKey(3, "foo", 4), 0.5, FIXED_DATETIME))

class VertexQueryTestCase(unittest.TestCase):
    def test_all(self):
        query = VertexQuery.all("foo")
        self.assertEqual(query.to_dict(), dict(type="all", start_id="foo", limit=1000))

    def test_vertex(self):
        query = VertexQuery.vertex("foo")
        self.assertEqual(query.to_dict(), dict(type="vertex", id="foo"))

    def test_vertices(self):
        query = VertexQuery.vertices(["foo", "bar", "baz"])
        self.assertEqual(query.to_dict(), dict(type="vertices", ids=["foo", "bar", "baz"]))

    def test_outbound_edges(self):
        query = VertexQuery.vertex("foo").outbound_edges(type_filter="bar", high_filter=FIXED_DATETIME, low_filter=FIXED_DATETIME)
        self.assertEqual(query.to_dict(), dict(
            type="pipe",
            vertex_query=dict(type="vertex", id="foo"),
            converter="outbound",
            type_filter="bar",
            high_filter="2017-04-10T23:20:00+00:00",
            low_filter="2017-04-10T23:20:00+00:00",
            limit=1000
        ))

    def test_inbound_edges(self):
        query = VertexQuery.vertex("foo").inbound_edges(type_filter="bar", high_filter=FIXED_DATETIME, low_filter=FIXED_DATETIME)
        self.assertEqual(query.to_dict(), dict(
            type="pipe",
            vertex_query=dict(type="vertex", id="foo"),
            converter="inbound",
            type_filter="bar",
            high_filter="2017-04-10T23:20:00+00:00",
            low_filter="2017-04-10T23:20:00+00:00",
            limit=1000
        ))

class EdgeQueryTestCase(unittest.TestCase):
    def test_edge(self):
        query = EdgeQuery.edge(EdgeKey("foo", "bar", "baz"))
        self.assertEqual(query.to_dict(), dict(type="edge", key=dict(outbound_id="foo", type="bar", inbound_id="baz")))

    def test_edges(self):
        query = EdgeQuery.edges([
            EdgeKey("foo1", "bar1", "baz1"),
            EdgeKey("foo2", "bar2", "baz2"),
        ])
        self.assertEqual(query.to_dict(), dict(type="edges", keys=[
            dict(outbound_id="foo1", type="bar1", inbound_id="baz1"),
            dict(outbound_id="foo2", type="bar2", inbound_id="baz2"),
        ]))

    def test_outbound_vertices(self):
        query = EdgeQuery.edge(EdgeKey("foo", "bar", "baz")).outbound_vertices()
        self.assertEqual(query.to_dict(), dict(
            type="pipe",
            edge_query=dict(type="edge", key=dict(outbound_id="foo", type="bar", inbound_id="baz")),
            converter="outbound",
            limit=1000
        ))

    def test_inbound_vertices(self):
        query = EdgeQuery.edge(EdgeKey("foo", "bar", "baz")).inbound_vertices()
        self.assertEqual(query.to_dict(), dict(
            type="pipe",
            edge_query=dict(type="edge", key=dict(outbound_id="foo", type="bar", inbound_id="baz")),
            converter="inbound",
            limit=1000
        ))
