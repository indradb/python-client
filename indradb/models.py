import json
import uuid
import datetime

from .hook import get_schema

capnp, indradb_capnp = get_schema()

class Utc(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

UTC = Utc()
EPOCH = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=UTC)
NANOS_PER_SEC = 1000000000

def to_timestamp(dt):
    return (dt - EPOCH).total_seconds() * NANOS_PER_SEC

def from_timestamp(ts):
    return datetime.datetime.utcfromtimestamp(ts / NANOS_PER_SEC).replace(tzinfo=UTC)

class _BaseModel(object):
    def __eq__(self, other):
        for key in self.__slots__:
            if not hasattr(other, key):
                return False
            if getattr(self, key) != getattr(other, key):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class Vertex(_BaseModel):
    """A vertex, which represents things. Vertices have types and UUIDs."""

    __slots__ = ["id", "t"]

    def __init__(self, id, t):
        """
        Creates a new vertex.

        `id` is the vertex UUID. `t` is the vertex type.
        """

        self.id = id
        self.t = t

    def to_message(self):
        return indradb_capnp.Vertex.new_message(
            id=self.id.bytes,
            t=self.t
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            id=uuid.UUID(bytes=message.id),
            t=message.t
        )

class EdgeKey(_BaseModel):
    """Identifies an edge."""

    __slots__ = ["outbound_id", "t", "inbound_id"]

    def __init__(self, outbound_id, t, inbound_id):
        """
        Creates a new edge key.
        
        `outbound_id` is the vertex UUID from which the edge is outbounding.
        `t` is the edge type. `inbound_id` is the vertex UUID into which
        the edge is inbounding.
        """

        self.outbound_id = outbound_id
        self.t = t
        self.inbound_id = inbound_id

    def to_message(self):
        return indradb_capnp.EdgeKey.new_message(
            outboundId=self.outbound_id.bytes,
            t=self.t,
            inboundId=self.inbound_id.bytes
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            outbound_id=uuid.UUID(bytes=message.outboundId),
            t=message.t,
            inbound_id=uuid.UUID(bytes=message.inboundId)
        )

class Edge(_BaseModel):
    """
    An edge, which represents a relationship between things, and have types
    and when they were last updated.
    """

    __slots__ = ["key", "created_datetime"]

    def __init__(self, key, created_datetime):
        """
        Creates a new edge.

        `key` is the `EdgeKey` to the edge. `created_datetime` is when the
        edge was created.
        """

        self.key = key
        self.created_datetime = created_datetime

    def to_message(self):
        return indradb_capnp.Edge.new_message(
            key=self.key.to_message(),
            createdDatetime=to_timestamp(self.created_datetime)
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            key=EdgeKey.from_message(message.key),
            created_datetime=from_timestamp(message.createdDatetime)
        )

class VertexProperty(_BaseModel):
    """
    Property attached to a vertex
    """

    __slots__ = ["id", "value"]

    def __init__(self, id, value):
        """
        Creates a new vertex property.

        `id` is the vertex ID that the property is attached to. `value`
        represents the property value.
        """

        self.id = id
        self.value = value

    @classmethod
    def from_message(cls, message):
        return cls(
            id=uuid.UUID(bytes=message.id),
            value=json.loads(message.value)
        )

class EdgeProperty(_BaseModel):
    """
    Property attached to an edge
    """

    __slots__ = ["key", "value"]

    def __init__(self, key, value):
        """
        Creates a new edge property.

        `key` is the edge key that the property is attached to. `value`
        represents the property value.
        """

        self.key = key
        self.value = value

    @classmethod
    def from_message(cls, message):
        return cls(
            key=EdgeKey.from_message(message.key),
            value=json.loads(message.value)
        )

class _VertexQuery(_BaseModel):
    def outbound(self, limit):
        """
        Get the edges outbounding from the vertices returned by this query.

        `limit` limits the number of returned edges.
        """
        return PipeEdgeQuery(self, "outbound", limit)

    def inbound(self, limit):
        """
        Get the edges inbounding from the vertices returned by this query.

        `limit` limits the number of returned edges.
        """
        return PipeEdgeQuery(self, "inbound", limit)

    def property(self, name):
        return VertexPropertyQuery(self, name)

class RangeVertexQuery(_VertexQuery):
    __slots__ = ["_limit", "_start_id", "_t"]

    def __init__(self, limit):
        self._limit = limit
        self._start_id = None
        self._t = None

    def start_id(self, value):
        self._start_id = value
        return self

    def t(self, value):
        self._t = value
        return self

    def to_message(self):
        message = indradb_capnp.VertexQuery.new_message()
        q = message.init("range")
        q.startId = self._start_id.bytes if self._start_id is not None else b""
        q.limit = self._limit
        q.t = self._t or ""
        return message

class SpecificVertexQuery(_VertexQuery):
    __slots__ = ["_ids"]

    def __init__(self, *ids):
        self._ids = ids

    def to_message(self):
        message = indradb_capnp.VertexQuery.new_message()
        q = message.init("specific")
        ids = q.init("ids", len(self._ids))

        for i, id in enumerate(self._ids):
            ids[i] = id.bytes

        return message

class PipeVertexQuery(_VertexQuery):
    __slots__ = ["_inner", "_direction", "_limit", "_t"]

    def __init__(self, inner, direction, limit):
        self._inner = inner
        self._direction = direction
        self._limit = limit
        self._t = None

    def t(self, value):
        self._t = value
        return self

    def to_message(self):
        message = indradb_capnp.VertexQuery.new_message()
        q = message.init("pipe")
        q.inner = self._inner.to_message()
        q.direction = self._direction
        q.limit = self._limit
        q.t = self._t or ""
        return message

class VertexPropertyQuery(_BaseModel):
    __slots__ = ["_inner", "_name"]

    def __init__(self, inner, name):
        self._inner = inner
        self._name = name

    def to_message(self):
        message = indradb_capnp.VertexPropertyQuery.new_message()
        message.inner = self._inner.to_message()
        message.name = self._name
        return message

class _EdgeQuery(_BaseModel):
    def outbound(self, limit):
        """
        Get the vertices outbounding from the edges returned by this query.

        `limit` limits the number of returned vertices.
        """
        return PipeVertexQuery(self, "outbound", limit)

    def inbound(self, limit):
        """
        Get the vertices inbounding from the edges returned by this query.

        `limit` limits the number of returned vertices.
        """
        return PipeVertexQuery(self, "inbound", limit)

    def property(self, name):
        return EdgePropertyQuery(self, name)

class SpecificEdgeQuery(_EdgeQuery):
    __slots__ = ["_keys"]

    def __init__(self, *keys):
        self._keys = keys

    def to_message(self):
        message = indradb_capnp.EdgeQuery.new_message()
        q = message.init("specific")
        keys = q.init("keys", len(self._keys))

        for i, key in enumerate(self._keys):
            keys[i] = key.to_message()

        return message

class PipeEdgeQuery(_EdgeQuery):
    __slots__ = ["_inner", "_direction", "_limit", "_t", "_high", "_low"]

    def __init__(self, inner, direction, limit):
        self._inner = inner
        self._direction = direction
        self._limit = limit
        self._t = None
        self._high = None
        self._low = None

    def t(self, value):
        self._t = value
        return self

    def high(self, value):
        self._high = value
        return self

    def low(self, value):
        self._low = value
        return value

    def to_message(self):
        message = indradb_capnp.EdgeQuery.new_message()
        q = message.init("pipe")
        q.inner = self._inner.to_message()
        q.direction = self._direction
        q.limit = self._limit
        q.t = self._t or ""
        q.high = to_timestamp(self._high) if self._high else 0
        q.low = to_timestamp(self._low) if self._low else 0
        return message

class EdgePropertyQuery(_BaseModel):
    __slots__ = ["_inner", "_name"]

    def __init__(self, inner, name):
        self._inner = inner
        self._name = name

    def to_message(self):
        message = indradb_capnp.EdgePropertyQuery.new_message()
        message.inner = self._inner.to_message()
        message.name = self._name
        return message

class BulkInsertVertex(_BaseModel):
    __slots__ = ["vertex"]

    def __init__(self, vertex):
        self.vertex = vertex

    def to_message(self):
        message = indradb_capnp.BulkInsertItem.new_message()
        container = message.init("vertex")
        container.vertex = self.vertex.to_message()
        return message

class BulkInsertEdge(_BaseModel):
    __slots__ = ["key"]

    def __init__(self, key):
        self.key = key

    def to_message(self):
        message = indradb_capnp.BulkInsertItem.new_message()
        container = message.init("edge")
        container.key = self.key.to_message()
        return message

class BulkInsertVertexProperty(_BaseModel):
    __slots__ = ["id", "name", "value"]

    def __init__(self, id, name, value):
        self.id = id
        self.name = name
        self.value = value

    def to_message(self):
        message = indradb_capnp.BulkInsertItem.new_message()
        container = message.init("vertexProperty")
        container.id = self.id.bytes
        container.name = self.name
        container.value = json.dumps(self.value)
        return message

class BulkInsertEdgeProperty(_BaseModel):
    __slots__ = ["key", "name", "value"]

    def __init__(self, key, name, value):
        self.key = key
        self.name = name
        self.value = value

    def to_message(self):
        message = indradb_capnp.BulkInsertItem.new_message()
        container = message.init("edgeProperty")
        container.key = self.key.to_message()
        container.name = self.name
        container.value = json.dumps(self.value)
        return message

class Property(_BaseModel):
    """
    List of properties attached to a vertex.
    """

    __slots__ = ["name", "value"]

    def __init__(self, name, value):
        """
        Creates a new property.

        `name` is the string name of the property, and `value` is its JSON value.
        """

        self.name = name
        self.value = value

    @classmethod
    def from_message(cls, message):
        return cls(
            name=message.name,
            value=json.loads(message.value)
        )

class VertexProperties(_BaseModel):
    """
    List of properties attached to a vertex.
    """

    __slots__ = ["vertex", "props"]

    def __init__(self, vertex, props):
        """
        Creates a new vertex properties.

        `vertex` is the vertex object, and `props` is a list of `Property`
        objects.
        """

        self.vertex = vertex
        self.props = props

    @classmethod
    def from_message(cls, message):
        return cls(
            vertex=Vertex.from_message(message.vertex),
            props=[Property.from_message(m) for m in message.props],
        )

class EdgeProperties(_BaseModel):
    """
    List of properties attached to an edge.
    """

    __slots__ = ["edge", "props"]

    def __init__(self, edge, props):
        """
        Creates a new edge properties.

        `edge` is the edge object, and `props` is a list of `Property`
        objects.
        """

        self.edge = edge
        self.props = props

    @classmethod
    def from_message(cls, message):
        return cls(
            edge=Edge.from_message(message.edge),
            props=[Property.from_message(m) for m in message.props],
        )
