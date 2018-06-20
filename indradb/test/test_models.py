import capnp
import indradb_capnp

import os
import uuid
import datetime
import unittest

from indradb import Vertex, EdgeKey, Edge, VertexQuery, EdgeQuery

class Utc(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

UTC = Utc()
FIXED_DATETIME = datetime.datetime(year=2018, month=6, day=20, hour=6, minute=25, second=0, tzinfo=UTC)
FIXED_TIMESTAMP = 1.5294759e+18

class VertexTestCase(unittest.TestCase):
    def test_to_message(self):
        id = uuid.uuid1()
        vertex = Vertex(id, "foo")
        message = vertex.to_message()
        self.assertEqual(message.id, id.bytes)
        self.assertEqual(message.type, "foo")

    def test_from_message(self):
        id = uuid.uuid1()

        message = indradb_capnp.Vertex.new_message(
            id=id.bytes,
            type="foo"
        )

        self.assertEqual(Vertex.from_message(message), Vertex(id, "foo"))

class EdgeKeyTestCase(unittest.TestCase):
    def test_to_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()
        key = EdgeKey(outbound_id, "foo", inbound_id)
        message = key.to_message()
        self.assertEqual(message.outboundId, outbound_id.bytes)
        self.assertEqual(message.type, "foo")
        self.assertEqual(message.inboundId, inbound_id.bytes)

    def test_from_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()

        message = indradb_capnp.EdgeKey.new_message(
            outboundId=outbound_id.bytes,
            type="foo",
            inboundId=inbound_id.bytes
        )

        self.assertEqual(EdgeKey.from_message(message), EdgeKey(outbound_id, "foo", inbound_id))

class EdgeTestCase(unittest.TestCase):
    def test_to_message(self):
        edge = Edge(EdgeKey(uuid.uuid1(), "foo", uuid.uuid1()), FIXED_DATETIME)
        message = edge.to_message()

        # EdgeKey is already validated in another test case, so we skip that.
        self.assertIsNotNone(message.key)
        self.assertAlmostEqual(message.createdDatetime, FIXED_TIMESTAMP)

    def test_from_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()
        key = EdgeKey(outbound_id, "foo", inbound_id)

        message = indradb_capnp.Edge.new_message(
            key=key.to_message(),
            createdDatetime=FIXED_TIMESTAMP
        )

        self.assertEqual(Edge.from_message(message), Edge(key, FIXED_DATETIME))

class VertexQueryTestCase(unittest.TestCase):
    def test_all(self):
        query = VertexQuery.all()
        message = query.to_message()
        self.assertEqual(message.all.startId, b"")
        self.assertEqual(message.all.limit, 0)

    def test_vertices(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        query = VertexQuery.vertices([id1, id2, id3])
        message = query.to_message()
        self.assertEqual(message.vertices.ids[0], id1.bytes)
        self.assertEqual(message.vertices.ids[1], id2.bytes)
        self.assertEqual(message.vertices.ids[2], id3.bytes)

    def test_outbound_edges(self):
        id = uuid.uuid1()
        query = VertexQuery.vertices([id]).outbound_edges(type_filter="bar", high_filter=FIXED_DATETIME)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.vertexQuery)
        self.assertEqual(message.pipe.converter, "outbound")
        self.assertEqual(message.pipe.typeFilter, "bar")
        self.assertAlmostEqual(message.pipe.highFilter, FIXED_TIMESTAMP)
        self.assertEqual(message.pipe.lowFilter, 0)
        self.assertEqual(message.pipe.limit, 0)
        
    def test_inbound_edges(self):
        id = uuid.uuid1()
        query = VertexQuery.vertices([id]).inbound_edges(type_filter="bar", high_filter=FIXED_DATETIME)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.vertexQuery)
        self.assertEqual(message.pipe.converter, "inbound")
        self.assertEqual(message.pipe.typeFilter, "bar")
        self.assertAlmostEqual(message.pipe.highFilter, FIXED_TIMESTAMP)
        self.assertEqual(message.pipe.lowFilter, 0)
        self.assertEqual(message.pipe.limit, 0)

class EdgeQueryTestCase(unittest.TestCase):
    def test_edges(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        query = EdgeQuery.edges([
            EdgeKey(id1, "bar1", id2),
            EdgeKey(id2, "bar2", id3)
        ])
        message = query.to_message()
        self.assertEqual(message.edges.keys[0].outboundId, id1.bytes)
        self.assertEqual(message.edges.keys[0].type, "bar1")
        self.assertEqual(message.edges.keys[0].inboundId, id2.bytes)
        self.assertEqual(message.edges.keys[1].outboundId, id2.bytes)
        self.assertEqual(message.edges.keys[1].type, "bar2")
        self.assertEqual(message.edges.keys[1].inboundId, id3.bytes)

    def test_outbound_vertices(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        query = EdgeQuery.edges([EdgeKey(id1, "bar", id2)]).outbound_vertices()
        message = query.to_message()
        self.assertIsNotNone(message.pipe.edgeQuery)
        self.assertEqual(message.pipe.converter, "outbound")
        self.assertEqual(message.pipe.limit, 0)

    def test_inbound_vertices(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        query = EdgeQuery.edges([EdgeKey(id1, "bar", id2)]).inbound_vertices()
        message = query.to_message()
        self.assertIsNotNone(message.pipe.edgeQuery)
        self.assertEqual(message.pipe.converter, "inbound")
        self.assertEqual(message.pipe.limit, 0)
