import json
import uuid
from enum import Enum

from indradb import proto

MAX_LIMIT = 2 ** 32 - 1
_SENTINAL = object()

class _BaseModel(object):
    def __eq__(self, other):
        for key in self.__slots__:
            if getattr(self, key) != getattr(other, key, _SENTINAL):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class Edge(_BaseModel):
    """Identifies an edge."""

    __slots__ = ["outbound_id", "t", "inbound_id"]

    def __init__(self, outbound_id, t, inbound_id):
        """
        Creates a new edge.
        
        `outbound_id` is the vertex UUID from which the edge is outbounding.
        `t` is the edge type. `inbound_id` is the vertex UUID into which
        the edge is inbounding.
        """

        self.outbound_id = outbound_id
        self.t = t
        self.inbound_id = inbound_id

    def to_message(self):
        return proto.Edge(
            outbound_id=proto.Uuid(value=self.outbound_id.bytes),
            t=proto.Identifier(value=self.t),
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

        `id` is the vertex UUID. `t` is the vertex identifier.
        """

        self.id = id
        self.t = t

    def to_message(self):
        return proto.Vertex(
            id=proto.Uuid(value=self.id.bytes),
            t=proto.Identifier(value=self.t),
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            id=uuid.UUID(bytes=message.id.value),
            t=message.t.value
        )

class _Query(_BaseModel):
    def outbound(self):
        """Gets the outbound vertices or edges associated with this query."""
        return PipeQuery(self, EdgeDirection.OUTBOUND)

    def inbound(self):
        """Gets the inbound vertices or edges associated with this query."""
        return PipeQuery(self, EdgeDirection.INBOUND)

    def with_property(self, name):
        """
        Gets values with a property.
        
        # Arguments
        * `name`: The name of the property.
        """
        return PipeWithPropertyPresenceQuery(self, name, True)

    def without_property(self, name):
        """
        Gets values without a property.
        
        # Arguments
        * `name`: The name of the property.
        """
        return PipeWithPropertyPresenceQuery(self, name, False)

    def with_property_equal_to(self, name, value):
        """
        Gets values with a property equal to a given value.
        
        # Arguments
        * `name`: The name of the property.
        * `value`: The value of the property.
        """
        return PipeWithPropertyValueQuery(self, name, value, True)

    def with_property_not_equal_to(self, name, value):
        """
        Gets values with a property not equal to a given value.
        
        # Arguments
        * `name`: The name of the property.
        * `value`: The value of the property.
        """
        return PipeWithPropertyValueQuery(self, name, value, False)

    def properties(self):
        """Gets the properties associated with the query results."""
        return PipePropertyQuery(self)

    def include(self):
        """
        Include this query's output, even if it is an intermediate result.
        """
        return IncludeQuery(self)

class _CountQuery:
    def count(self):
        return CountQuery(self)

class AllVertexQuery(_Query, _CountQuery):
    """Gets all vertices."""
    def to_message(self):
        return proto.Query(all_vertex=proto.google_dot_protobuf_dot_empty__pb2.Empty())

class RangeVertexQuery(_Query):
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
        return proto.Query(
            range_vertex=proto.RangeVertexQuery(
                limit=self._limit,
                t=proto.Identifier(value=self._t) if self._t is not None else None,
                start_id=proto.Uuid(value=self._start_id.bytes) if self._start_id is not None else None,
            ),
        )

class SpecificVertexQuery(_Query):
    """Gets a specific set of vertices."""
    __slots__ = ["_ids"]

    def __init__(self, *ids):
        self._ids = ids

    def to_message(self):
        return proto.Query(
            specific_vertex=proto.SpecificVertexQuery(ids=[proto.Uuid(value=i.bytes) for i in self._ids]),
        )

class VertexWithPropertyPresenceQuery(_Query):
    """Gets vertices with or without a given property."""
    __slots__ = ["_name"]

    def __init__(self, name):
        self._name = name

    def to_message(self):
        return proto.Query(
            vertex_with_property_presence=proto.VertexWithPropertyPresenceQuery(
                name=proto.Identifier(value=self._name),
            ),
        )

class VertexWithPropertyValueQuery(_Query):
    """Gets vertices with a property equal to a given value."""
    __slots__ = ["_name", "_value"]

    def __init__(self, _name, _value):
        self._name = name
        self._value = value

    def to_message(self):
        return proto.Query(
            vertex_with_property_value=proto.VertexWithPropertyValueQuery(
                name=proto.Identifier(value=self._name),
                value=json.dumps(self._value),
            ),
        )

class AllEdgeQuery(_Query, _CountQuery):
    """Gets all edges."""
    def to_message(self):
        return proto.Query(all_edge=proto.google_dot_protobuf_dot_empty__pb2.Empty())

class SpecificEdgeQuery(_Query):
    """Gets a specific set of edges."""
    __slots__ = ["_edges"]

    def __init__(self, *edges):
        self._edges = edges

    def to_message(self):
        return proto.Query(
            specific_edge=proto.SpecificEdgeQuery(edges=[e.to_message() for e in self._edges]),
        )

class EdgeWithPropertyPresenceQuery(_Query):
    """Gets edges with or without a given property."""
    __slots__ = ["_name"]

    def __init__(self, name):
        self._name = name

    def to_message(self):
        return proto.Query(
            edge_with_property_presence=proto.EdgeWithPropertyPresenceQuery(
                name=proto.Identifier(value=self._name),
            ),
        )

class EdgeWithPropertyValueQuery(_Query):
    """Gets edges with a property equal to a given value."""
    __slots__ = ["_name", "_value"]

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def to_message(self):
        return proto.Query(
            edge_with_property_value=proto.EdgeWithPropertyValueQuery(
                name=proto.Identifier(value=self._name),
                value=json.dumps(self._value),
            ),
        )

class PipeQuery(_Query):
    """
    Gets the vertices associated with edges, or edges associated with
    vertices.
    
    Generally, you shouldn't need to construct this directly, but rather call
    `.outbound()` or `.inbound()`.
    """
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
        return proto.Query(
            pipe=proto.PipeQuery(
                inner=self._inner.to_message(),
                direction=self._direction.value,
                limit=self._limit,
                t=proto.Identifier(value=self._t) if self._t is not None else None,
            ),
        )

class PipePropertyQuery(_Query, _CountQuery):
    """Returns the properties associated with a vertex or edge."""
    __slots__ = ["_inner", "_name"]

    def __init__(self, inner):
        self._inner = inner
        self._name = None

    def name(self, value):
        self._name = value
        return self

    def to_message(self):
        return proto.Query(
            pipe_property=proto.PipePropertyQuery(
                inner=self._inner.to_message(),
                name=proto.Identifier(value=self._name) if self._name is not None else None,
            )
        )

class PipeWithPropertyPresenceQuery(_Query):
    """Gets vertices or edges with or without a property."""
    __slots__ = ["_inner", "_name", "_exists"]

    def __init__(self, inner, name, exists):
        self._inner = inner
        self._name = name
        self._exists = exists

    def to_message(self):
        return proto.Query(
            pipe_with_property_presence=proto.PipeWithPropertyPresenceQuery(
                inner=self._inner.to_message(),
                name=proto.Identifier(value=self._name),
                exists=self._exists,
            ),
        )

class PipeWithPropertyValueQuery(_Query):
    """Gets vertices or edges with a property equal to a given value."""
    __slots__ = ["_inner", "_name", "_value", "_equal"]

    def __init__(self, inner, name, value, equal):
        self._inner = inner
        self._name = name
        self._value = value
        self._equal = equal

    def to_message(self):
        return proto.Query(
            pipe_with_property_value=proto.PipeWithPropertyValueQuery(
                inner=self._inner.to_message(),
                name=proto.Identifier(value=self._name),
                value=json.dumps(self._value),
                equal=self._equal,
            ),
        )

class IncludeQuery(_Query):
    """
    Includes the results of a query in output.

    The outermost part of a query will always be explicitly included. This
    allows you to also output an intermediate result.
    """
    __slots__ = ["_inner"]

    def __init__(self, inner):
        self._inner = inner

    def to_message(self):
        return proto.Query(
            include=proto.IncludeQuery(
                inner=self._inner.to_message(),
            ),
        )

class CountQuery:
    """Counts the number of items returned from a query."""
    __slots__ = ["_inner"]

    def __init__(self, inner):
        self._inner = inner

    def to_message(self):
        return proto.Query(
            count=proto.CountQuery(
                inner=self._inner.to_message(),
            ),
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
            name=message.name.value,
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

    def __eq__(self, other):
        if self.vertex != getattr(other, "vertex", _SENTINAL):
            return False
        other_props = getattr(other, "props", _SENTINAL)
        if len(self.props) != len(other_props):
            return False
        return all(a == b for a, b in zip(self.props, other.props))

class EdgeProperty(_BaseModel):
    """
    Property attached to an edge
    """

    __slots__ = ["edge", "value"]

    def __init__(self, edge, value):
        """
        Creates a new edge property.

        `edge` is the edge that the property is attached to. `value`
        represents the property value.
        """

        self.edge = edge
        self.value = value

    @classmethod
    def from_message(cls, message):
        return cls(
            edge=Edge.from_message(message.edge),
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

    def __eq__(self, other):
        if self.edge != getattr(other, "edge", _SENTINAL):
            return False
        other_props = getattr(other, "props", _SENTINAL)
        if len(self.props) != len(other_props):
            return False
        return all(a == b for a, b in zip(self.props, other.props))
