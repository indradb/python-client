import json
import uuid
import datetime
from enum import Enum

from indradb import proto

MAX_LIMIT = 2 ** 32 - 1

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
        ts = proto.google_dot_protobuf_dot_timestamp__pb2.Timestamp()
        ts.FromDatetime(self.created_datetime)

        return proto.Edge(
            key=self.key.to_message(),
            created_datetime=ts,
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            key=EdgeKey.from_message(message.key),
            created_datetime=message.created_datetime.ToDatetime(),
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
        return proto.EdgeKey(
            outbound_id=proto.Uuid(value=self.outbound_id.bytes),
            t=proto.Type(value=self.t),
            inbound_id=proto.Uuid(value=self.inbound_id.bytes),
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            outbound_id=uuid.UUID(bytes=message.outbound_id.value),
            t=message.t.value,
            inbound_id=uuid.UUID(bytes=message.inbound_id.value),
        )

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
        return proto.Vertex(
            id=proto.Uuid(value=self.id.bytes),
            t=proto.Type(value=self.t),
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            id=uuid.UUID(bytes=message.id.value),
            t=message.t.value
        )

class _VertexQuery(_BaseModel):
    def outbound(self):
        """
        Get the edges outbounding from the vertices returned by this query.
        """
        return PipeEdgeQuery(self, EdgeDirection.OUTBOUND)

    def inbound(self):
        """
        Get the edges inbounding from the vertices returned by this query.
        """
        return PipeEdgeQuery(self, EdgeDirection.INBOUND)

    def property(self, name):
        return VertexPropertyQuery(self, name)

class RangeVertexQuery(_VertexQuery):
    __slots__ = ["_limit", "_start_id", "_t"]

    def __init__(self):
        self._limit = MAX_LIMIT
        self._start_id = None
        self._t = None

    def limit(self, value):
        self._limit = value
        return self

    def start_id(self, value):
        self._start_id = value
        return self

    def t(self, value):
        self._t = value
        return self

    def to_message(self):
        return proto.VertexQuery(
            range=proto.RangeVertexQuery(
                limit=self._limit,
                t=proto.Type(value=self._t) if self._t is not None else None,
                start_id=proto.Uuid(value=self._start_id.bytes) if self._start_id is not None else None,
            ),
        )

class SpecificVertexQuery(_VertexQuery):
    __slots__ = ["_ids"]

    def __init__(self, *ids):
        self._ids = ids

    def to_message(self):
        return proto.VertexQuery(
            specific=proto.SpecificVertexQuery(ids=[proto.Uuid(value=i.bytes) for i in self._ids]),
        )

class PipeVertexQuery(_VertexQuery):
    __slots__ = ["_inner", "_direction", "_limit", "_t"]

    def __init__(self, inner, direction):
        self._inner = inner
        self._direction = direction
        self._limit = MAX_LIMIT
        self._t = None

    def limit(self, value):
        self._limit = value
        return self

    def t(self, value):
        self._t = value
        return self

    def to_message(self):
        return proto.VertexQuery(
            pipe=proto.PipeVertexQuery(
                inner=self._inner.to_message(),
                direction=self._direction.value,
                limit=self._limit,
                t=proto.Type(value=self._t) if self._t is not None else None,
            ),
        )

class VertexPropertyQuery(_BaseModel):
    __slots__ = ["_inner", "_name"]

    def __init__(self, inner, name):
        self._inner = inner
        self._name = name

    def to_message(self):
        return proto.VertexPropertyQuery(
            inner=self._inner.to_message(),
            name=self._name,
        )

class _EdgeQuery(_BaseModel):
    def outbound(self):
        """
        Get the vertices outbounding from the edges returned by this query.
        """
        return PipeVertexQuery(self, EdgeDirection.OUTBOUND)

    def inbound(self):
        """
        Get the vertices inbounding from the edges returned by this query.
        """
        return PipeVertexQuery(self, EdgeDirection.INBOUND)

    def property(self, name):
        return EdgePropertyQuery(self, name)

class SpecificEdgeQuery(_EdgeQuery):
    __slots__ = ["_keys"]

    def __init__(self, *keys):
        self._keys = keys

    def to_message(self):
        return proto.EdgeQuery(
            specific=proto.SpecificEdgeQuery(keys=[k.to_message() for k in self._keys]),
        )

class PipeEdgeQuery(_EdgeQuery):
    __slots__ = ["_inner", "_direction", "_limit", "_t", "_high", "_low"]

    def __init__(self, inner, direction):
        self._inner = inner
        self._direction = direction
        self._limit = MAX_LIMIT
        self._t = None
        self._high = None
        self._low = None

    def limit(self, value):
        self._limit = value
        return self

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
        high = None
        if self._high is not None:
            high = proto.google_dot_protobuf_dot_timestamp__pb2.Timestamp()
            high.FromDatetime(self._high)

        low = None
        if self._low is not None:
            low = proto.google_dot_protobuf_dot_timestamp__pb2.Timestamp()
            low.FromDatetime(self._low)

        return proto.EdgeQuery(
            pipe=proto.PipeEdgeQuery(
                inner=self._inner.to_message(),
                direction=self._direction.value,
                t=proto.Type(value=self._t) if self._t is not None else None,
                high=high,
                low=low,
                limit=self._limit,
            ),
        )

class EdgePropertyQuery(_BaseModel):
    __slots__ = ["_inner", "_name"]

    def __init__(self, inner, name):
        self._inner = inner
        self._name = name

    def to_message(self):
        return proto.EdgePropertyQuery(
            inner=self._inner.to_message(),
            name=self._name,
        )

class EdgeDirection(Enum):
    OUTBOUND = proto.OUTBOUND
    INBOUND = proto.INBOUND

class NamedProperty(_BaseModel):
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
            value=json.loads(message.value.value),
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
            id=uuid.UUID(bytes=message.id.value),
            value=json.loads(message.value.value)
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
            props=[NamedProperty.from_message(p) for p in message.props],
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
            value=json.loads(message.value.value),
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
            props=[NamedProperty.from_message(p) for p in message.props],
        )
