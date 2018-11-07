import os
import uuid
import datetime
import unittest

from indradb import *
from indradb.hook import get_schema

capnp, indradb_capnp = get_schema()

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
        self.assertEqual(message.t, "foo")

    def test_from_message(self):
        id = uuid.uuid1()

        message = indradb_capnp.Vertex.new_message(
            id=id.bytes,
            t="foo"
        )

        self.assertEqual(Vertex.from_message(message), Vertex(id, "foo"))

class EdgeKeyTestCase(unittest.TestCase):
    def test_to_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()
        key = EdgeKey(outbound_id, "foo", inbound_id)
        message = key.to_message()
        self.assertEqual(message.outboundId, outbound_id.bytes)
        self.assertEqual(message.t, "foo")
        self.assertEqual(message.inboundId, inbound_id.bytes)

    def test_from_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()

        message = indradb_capnp.EdgeKey.new_message(
            outboundId=outbound_id.bytes,
            t="foo",
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
    def test_range(self):
        query = RangeVertexQuery(1000)
        message = query.to_message()
        self.assertEqual(message.range.startId, b"")
        self.assertEqual(message.range.limit, 1000)

    def test_specific(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        query = SpecificVertexQuery(id1, id2, id3)
        message = query.to_message()
        self.assertEqual(message.specific.ids[0], id1.bytes)
        self.assertEqual(message.specific.ids[1], id2.bytes)
        self.assertEqual(message.specific.ids[2], id3.bytes)

    def test_outbound(self):
        id = uuid.uuid1()
        query = SpecificVertexQuery(id).outbound(20).t("bar").high(FIXED_DATETIME)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.inner)
        self.assertEqual(message.pipe.direction, "outbound")
        self.assertEqual(message.pipe.t, "bar")
        self.assertAlmostEqual(message.pipe.high, FIXED_TIMESTAMP)
        self.assertEqual(message.pipe.low, 0)
        self.assertEqual(message.pipe.limit, 20)
        
    def test_inbound(self):
        id = uuid.uuid1()
        query = SpecificVertexQuery(id).inbound(30).t("bar").high(FIXED_DATETIME)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.inner)
        self.assertEqual(message.pipe.direction, "inbound")
        self.assertEqual(message.pipe.t, "bar")
        self.assertAlmostEqual(message.pipe.high, FIXED_TIMESTAMP)
        self.assertEqual(message.pipe.low, 0)
        self.assertEqual(message.pipe.limit, 30)

class EdgeQueryTestCase(unittest.TestCase):
    def test_edges(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()

        query = SpecificEdgeQuery(
            EdgeKey(id1, "bar1", id2),
            EdgeKey(id2, "bar2", id3)
        )
        
        message = query.to_message()
        self.assertEqual(message.specific.keys[0].outboundId, id1.bytes)
        self.assertEqual(message.specific.keys[0].t, "bar1")
        self.assertEqual(message.specific.keys[0].inboundId, id2.bytes)
        self.assertEqual(message.specific.keys[1].outboundId, id2.bytes)
        self.assertEqual(message.specific.keys[1].t, "bar2")
        self.assertEqual(message.specific.keys[1].inboundId, id3.bytes)

    def test_outbound(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        query = SpecificEdgeQuery(EdgeKey(id1, "bar", id2)).outbound(0)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.inner)
        self.assertEqual(message.pipe.direction, "outbound")
        self.assertEqual(message.pipe.limit, 0)

    def test_inbound_vertices(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        query = SpecificEdgeQuery(EdgeKey(id1, "bar", id2)).inbound(10)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.inner)
        self.assertEqual(message.pipe.direction, "inbound")
        self.assertEqual(message.pipe.limit, 10)
