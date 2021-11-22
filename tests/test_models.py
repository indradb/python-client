import os
import json
import uuid
import datetime
import unittest

from indradb import *

FIXED_DATETIME = datetime.datetime(year=2018, month=6, day=20, hour=6, minute=25, second=0)

class EdgeTestCase(unittest.TestCase):
    def test_to_message(self):
        edge = Edge(EdgeKey(uuid.uuid1(), "foo", uuid.uuid1()), FIXED_DATETIME)
        message = edge.to_message()
        # EdgeKey is already validated in another test case, so we skip that.
        self.assertIsNotNone(message.key)
        self.assertEqual(message.created_datetime.ToDatetime(), FIXED_DATETIME)

    def test_from_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()
        key = EdgeKey(outbound_id, "foo", inbound_id)
        ts = proto.google_dot_protobuf_dot_timestamp__pb2.Timestamp()
        ts.FromDatetime(FIXED_DATETIME)
        message = proto.Edge(
            key=key.to_message(),
            created_datetime=ts,
        )
        self.assertEqual(Edge.from_message(message), Edge(key, FIXED_DATETIME))

class EdgeKeyTestCase(unittest.TestCase):
    def test_to_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()
        key = EdgeKey(outbound_id, "foo", inbound_id)
        message = key.to_message()
        self.assertEqual(message.outbound_id.value, outbound_id.bytes)
        self.assertEqual(message.t.value, "foo")
        self.assertEqual(message.inbound_id.value, inbound_id.bytes)

    def test_from_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()
        message = proto.EdgeKey(
            outbound_id=proto.Uuid(value=outbound_id.bytes),
            t=proto.Type(value="foo"),
            inbound_id=proto.Uuid(value=inbound_id.bytes),
        )
        self.assertEqual(EdgeKey.from_message(message), EdgeKey(outbound_id, "foo", inbound_id))

class VertexTestCase(unittest.TestCase):
    def test_to_message(self):
        id = uuid.uuid1()
        vertex = Vertex(id, "foo")
        message = vertex.to_message()
        self.assertEqual(message.id.value, id.bytes)
        self.assertEqual(message.t.value, "foo")

    def test_from_message(self):
        id = uuid.uuid1()
        message = proto.Vertex(
            id=proto.Uuid(value=id.bytes),
            t=proto.Type(value="foo"),
        )
        self.assertEqual(Vertex.from_message(message), Vertex(id, "foo"))

class VertexQueryTestCase(unittest.TestCase):
    def test_range(self):
        query = RangeVertexQuery()
        message = query.to_message()
        self.assertEqual(message.range.start_id.value, b"")
        self.assertEqual(message.range.limit, 2 ** 32 - 1)

    def test_specific(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        query = SpecificVertexQuery(id1, id2, id3)
        message = query.to_message()
        self.assertEqual(message.specific.ids[0].value, id1.bytes)
        self.assertEqual(message.specific.ids[1].value, id2.bytes)
        self.assertEqual(message.specific.ids[2].value, id3.bytes)

    def test_outbound(self):
        id = uuid.uuid1()
        query = SpecificVertexQuery(id).outbound().limit(20).t("bar").high(FIXED_DATETIME)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.inner)
        self.assertEqual(message.pipe.direction, EdgeDirection.OUTBOUND.value)
        self.assertEqual(message.pipe.t.value, "bar")
        self.assertEqual(message.pipe.high.ToDatetime(), FIXED_DATETIME)
        self.assertFalse(message.pipe.HasField("low"))
        self.assertEqual(message.pipe.limit, 20)
        
    def test_inbound(self):
        id = uuid.uuid1()
        query = SpecificVertexQuery(id).inbound().limit(30).t("bar").high(FIXED_DATETIME)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.inner)
        self.assertEqual(message.pipe.direction, EdgeDirection.INBOUND.value)
        self.assertEqual(message.pipe.t.value, "bar")
        self.assertEqual(message.pipe.high.ToDatetime(), FIXED_DATETIME)
        self.assertFalse(message.pipe.HasField("low"))
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
        self.assertEqual(message.specific.keys[0].outbound_id.value, id1.bytes)
        self.assertEqual(message.specific.keys[0].t.value, "bar1")
        self.assertEqual(message.specific.keys[0].inbound_id.value, id2.bytes)
        self.assertEqual(message.specific.keys[1].outbound_id.value, id2.bytes)
        self.assertEqual(message.specific.keys[1].t.value, "bar2")
        self.assertEqual(message.specific.keys[1].inbound_id.value, id3.bytes)

    def test_outbound(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        query = SpecificEdgeQuery(EdgeKey(id1, "bar", id2)).outbound().limit(0)
        message = query.to_message()
        self.assertIsNotNone(message.pipe.inner)
        self.assertEqual(message.pipe.direction, EdgeDirection.OUTBOUND.value)
        self.assertEqual(message.pipe.limit, 0)

    def test_inbound_vertices(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        query = SpecificEdgeQuery(EdgeKey(id1, "bar", id2)).inbound()
        message = query.to_message()
        self.assertIsNotNone(message.pipe.inner)
        self.assertEqual(message.pipe.direction, EdgeDirection.INBOUND.value)
        self.assertEqual(message.pipe.limit, 2 ** 32 - 1)

class NamedPropertyTestCase(unittest.TestCase):
    def test_from_message(self):
        message = proto.NamedProperty(name="foo", value=proto.Json(value=json.dumps({})))
        self.assertEqual(NamedProperty.from_message(message), NamedProperty("foo", {}))

class VertexPropertyTestCase(unittest.TestCase):
    def test_from_message(self):
        id = uuid.uuid1()
        message = proto.VertexProperty(
            id=proto.Uuid(value=id.bytes),
            value=proto.Json(value=json.dumps(True))
        )
        self.assertEqual(VertexProperty.from_message(message), VertexProperty(id, True))

class VertexPropertiesTestCase(unittest.TestCase):
    def test_from_message(self):
        id = uuid.uuid1()
        message = proto.VertexProperties(
            vertex=proto.Vertex(
                id=proto.Uuid(value=id.bytes),
                t=proto.Type(value="foo"),
            ),
            props=[
                proto.NamedProperty(name="first", value=proto.Json(value=json.dumps(True))),
                proto.NamedProperty(name="second", value=proto.Json(value=json.dumps(False))),
            ],
        )
        self.assertEqual(VertexProperties.from_message(message), VertexProperties(Vertex(id, "foo"), [
            NamedProperty("first", True),
            NamedProperty("second", False),
        ]))

class EdgePropertyTestCase(unittest.TestCase):
    def test_from_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()
        message = proto.EdgeProperty(
            key=proto.EdgeKey(
                outbound_id=proto.Uuid(value=outbound_id.bytes),
                t=proto.Type(value="foo"),
                inbound_id=proto.Uuid(value=inbound_id.bytes),
            ),
            value=proto.Json(value=json.dumps("bar"))
        )
        self.assertEqual(EdgeProperty.from_message(message), EdgeProperty(EdgeKey(outbound_id, "foo", inbound_id), "bar"))

class EdgePropertiesTestCase(unittest.TestCase):
    def test_from_message(self):
        outbound_id = uuid.uuid1()
        inbound_id = uuid.uuid1()
        ts = proto.google_dot_protobuf_dot_timestamp__pb2.Timestamp()
        ts.FromDatetime(FIXED_DATETIME)
        message = proto.EdgeProperties(
            edge=proto.Edge(
                key=proto.EdgeKey(
                    outbound_id=proto.Uuid(value=outbound_id.bytes),
                    t=proto.Type(value="foo"),
                    inbound_id=proto.Uuid(value=inbound_id.bytes),
                ),
                created_datetime=ts,
            ),
            props=[
                proto.NamedProperty(name="first", value=proto.Json(value=json.dumps(True))),
                proto.NamedProperty(name="second", value=proto.Json(value=json.dumps(False))),
            ],
        )
        edge = Edge(EdgeKey(outbound_id, "foo", inbound_id), FIXED_DATETIME)
        self.assertEqual(EdgeProperties.from_message(message), EdgeProperties(edge, [
            NamedProperty("first", True),
            NamedProperty("second", False),
        ]))
