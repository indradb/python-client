import os
import unittest
import datetime

from braid import Vertex, EdgeKey, Edge, VertexQuery, EdgeQuery

FIXED_DATETIME = datetime.datetime(year=2017, month=4, day=10, hour=23, minute=20, second=0, tzinfo=datetime.timezone.utc)

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
            update_datetime="2017-04-10T23:20:00+00:00",
        ))

    def test_from_dict(self):
        d = dict(
            key=dict(outbound_id=3, type="foo", inbound_id=4),
            weight=0.5,
            update_datetime="2017-04-10T23:20:00",
        )
        self.assertEqual(Edge.from_dict(d), Edge(EdgeKey(3, "foo", 4), 0.5, FIXED_DATETIME))

class VertexQueryTestCase(unittest.TestCase):
    def test_all(self):
        query = VertexQuery.all("foo")
        self.assertEqual(query._query, dict(all=("foo", 1000)))

    def test_vertex(self):
        query = VertexQuery.vertex("foo")
        self.assertEqual(query._query, dict(vertex="foo"))

    def test_vertices(self):
        query = VertexQuery.vertices(["foo", "bar", "baz"])
        self.assertEqual(query._query, dict(vertices=["foo", "bar", "baz"]))

    def test_outbound_edges(self):
        query = VertexQuery.vertex("foo").outbound_edges(type="bar", high=FIXED_DATETIME, low=FIXED_DATETIME)
        self.assertEqual(query._query, dict(pipe=(dict(vertex="foo"), "outbound", "bar", "2017-04-10T23:20:00+00:00", "2017-04-10T23:20:00+00:00", 1000)))

    def test_inbound_edges(self):
        query = VertexQuery.vertex("foo").inbound_edges(type="bar", high=FIXED_DATETIME, low=FIXED_DATETIME)
        self.assertEqual(query._query, dict(pipe=(dict(vertex="foo"), "inbound", "bar", "2017-04-10T23:20:00+00:00", "2017-04-10T23:20:00+00:00", 1000)))

class EdgeQueryTestCase(unittest.TestCase):
    def test_edge(self):
        query = EdgeQuery.edge(EdgeKey("foo", "bar", "baz"))
        self.assertEqual(query._query, dict(edge=dict(outbound_id="foo", type="bar", inbound_id="baz")))

    def test_edges(self):
        query = EdgeQuery.edges([
            EdgeKey("foo1", "bar1", "baz1"),
            EdgeKey("foo2", "bar2", "baz2"),
        ])
        self.assertEqual(query._query, dict(edges=[
            dict(outbound_id="foo1", type="bar1", inbound_id="baz1"),
            dict(outbound_id="foo2", type="bar2", inbound_id="baz2"),
        ]))

    def test_outbound_vertices(self):
        query = EdgeQuery.edge(EdgeKey("foo", "bar", "baz")).outbound_vertices()
        edge_key_dict = dict(edge=dict(outbound_id="foo", type="bar", inbound_id="baz"))
        self.assertEqual(query._query, dict(pipe=(edge_key_dict, "outbound", 1000)))

    def test_inbound_vertices(self):
        query = EdgeQuery.edge(EdgeKey("foo", "bar", "baz")).inbound_vertices()
        edge_key_dict = dict(edge=dict(outbound_id="foo", type="bar", inbound_id="baz"))
        self.assertEqual(query._query, dict(pipe=(edge_key_dict, "inbound", 1000)))
