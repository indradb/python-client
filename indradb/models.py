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

class Vertex(object):
    """A vertex, which represents things. Vertices have types and UUIDs."""

    def __init__(self, id, type):
        """
        Creates a new vertex.

        `id` is the vertex UUID. `type` is the vertex type.
        """

        self.id = id
        self.type = type

    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return False
        if self.id != other.id:
            return False
        if self.type != other.type:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_message(self):
        return indradb_capnp.Vertex.new_message(
            id=self.id.bytes,
            type=self.type
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            id=uuid.UUID(bytes=message.id),
            type=message.type
        )

class EdgeKey(object):
    """Identifies an edge."""

    def __init__(self, outbound_id, type, inbound_id):
        """
        Creates a new edge key.
        
        `outbound_id` is the vertex UUID from which the edge is outbounding.
        `type` is the edge type. `inbound_id` is the vertex UUID into which
        the edge is inbounding.
        """

        self.outbound_id = outbound_id
        self.type = type
        self.inbound_id = inbound_id

    def __eq__(self, other):
        if not isinstance(other, EdgeKey):
            return False
        if self.outbound_id != other.outbound_id:
            return False
        if self.type != other.type:
            return False
        if self.inbound_id != other.inbound_id:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_message(self):
        return indradb_capnp.EdgeKey.new_message(
            outboundId=self.outbound_id.bytes,
            type=self.type,
            inboundId=self.inbound_id.bytes
        )

    @classmethod
    def from_message(cls, message):
        return cls(
            outbound_id=uuid.UUID(bytes=message.outboundId),
            type=message.type,
            inbound_id=uuid.UUID(bytes=message.inboundId)
        )

class Edge(object):
    """
    An edge, which represents a relationship between things, and have types
    and when they were last updated.
    """

    def __init__(self, key, created_datetime):
        """
        Creates a new edge.

        `key` is the `EdgeKey` to the edge. `created_datetime` is when the
        edge was created.
        """

        self.key = key
        self.created_datetime = created_datetime

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        if self.key != other.key:
            return False
        if self.created_datetime != other.created_datetime:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

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

class VertexProperty(object):
    """
    Property attached to a vertex
    """

    def __init__(self, id, value):
        """
        Creates a new vertex property.

        `id` is the vertex ID that the property is attached to. `value`
        represents the property value.
        """

        self.id = id
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, VertexProperty):
            return False
        if self.id != other.id:
            return False
        if self.value != other.value:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_message(cls, message):
        return cls(
            id=uuid.UUID(bytes=message.id),
            value=json.loads(message.value)
        )

class EdgeProperty(object):
    """
    Property attached to an edge
    """

    def __init__(self, key, value):
        """
        Creates a new edge property.

        `key` is the edge key that the property is attached to. `value`
        represents the property value.
        """

        self.key = key
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, EdgeProperty):
            return False
        if self.key != other.key:
            return False
        if self.value != other.value:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_message(cls, message):
        return cls(
            key=EdgeKey.from_message(message.key),
            value=json.loads(message.value)
        )

# NOTE: python's stdlib enums are not used because we want to support python
# 2.7, and they were introduced in 3.4.
class Enum(object):
    """Abstract class that represents an enum"""

    def __init__(self, type, **kwargs):
        """
        Creates a new enum. Generally you shouldn't construct a query objects
        directly, but rather use the class methods.
        """
        self.type = type
        self.payload = kwargs

    def __eq__(self, other):
        if self.type != getattr(other, "type"):
            return False
        if self.payload != getattr(other, "payload"):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class VertexQuery(Enum):
    """A query for vertices."""

    def to_message(self):
        message = indradb_capnp.VertexQuery.new_message()

        if self.type == "all":
            all = message.init("all")
            
            start_id = self.payload["start_id"]
            all.startId = start_id.bytes if start_id is not None else b""
            
            all.limit = self.payload["limit"]
        elif self.type == "vertices":
            payload_ids = self.payload["ids"]
            vertices = message.init("vertices")
            ids = vertices.init("ids", len(payload_ids))

            for i, id in enumerate(payload_ids):
                ids[i] = id.bytes
        elif self.type == "pipe":
            pipe = message.init("pipe")
            pipe.edgeQuery = self.payload["edge_query"].to_message()
            pipe.converter = self.payload["converter"]
            pipe.limit = self.payload["limit"]
        else:
            raise ValueError("Unknown type for vertex query")

        return message

    @classmethod
    def all(cls, limit, start_id=None):
        """
        Gets all vertices, filtered only the input arguments. Generally this
        query is useful when you want to iterate over all of the vertices in
        the datastore - e.g. to build an in-memory representation of the data.

        `limit` sets the limit of the number vertices to return. `start_id`
        represents the vertex UUID from which to start for the returned range
        (exclusive.) 
        """
        return cls("all", start_id=start_id, limit=limit)

    @classmethod
    def vertices(cls, ids):
        """
        Gets a set of vertices. Generally this query is useful when you have a
        set of vertices from a previous query upon which you want to construct
        a new query.

        `ids` is the set of vertex UUIDs to get.
        """
        return cls("vertices", ids=ids)

    def outbound_edges(self, limit, type_filter=None, high_filter=None, low_filter=None):
        """
        Get the edges outbounding from the vertices returned by this query.

        `limit` limits the number of returned edges. `type_filter` optionally
        filters those edges to only have a specific type. `high_filter`
        optionally filters those edges to only get ones updated at or before
        the given datetime. `low_filter` optionally filters those edges to
        only get ones updated at or after the given datetime.
        """
        return EdgeQuery(
            "pipe",
            vertex_query=self,
            converter="outbound",
            type_filter=type_filter,
            high_filter=high_filter,
            low_filter=low_filter,
            limit=limit
        )

    def inbound_edges(self, limit, type_filter=None, high_filter=None, low_filter=None):
        """
        Get the edges inbounding from the vertices returned by this query.

        `limit` limits the number of returned edges. `type_filter` optionally
        filters those edges to only have a specific type. `high_filter`
        optionally filters those edges to only get ones updated at or before
        the given datetime. `low_filter` optionally filters those edges to
        only get ones updated at or after the given datetime.
        """
        return EdgeQuery(
            "pipe",
            vertex_query=self,
            converter="inbound",
            type_filter=type_filter,
            high_filter=high_filter,
            low_filter=low_filter,
            limit=limit
        )

class EdgeQuery(Enum):
    """A query for edges."""

    def to_message(self):
        message = indradb_capnp.EdgeQuery.new_message()

        if self.type == "edges":
            payload_keys = self.payload["keys"]
            edges = message.init("edges")
            keys = edges.init("keys", len(payload_keys))

            for i, key in enumerate(payload_keys):
                keys[i] = key.to_message()
        elif self.type == "pipe":
            pipe = message.init("pipe")
            pipe.vertexQuery = self.payload["vertex_query"].to_message()
            pipe.converter = self.payload["converter"]

            type_filter = self.payload["type_filter"]
            pipe.typeFilter = type_filter if type_filter is not None else ""
            
            high_filter = self.payload["high_filter"]
            pipe.highFilter = to_timestamp(high_filter) if high_filter is not None else 0
            
            low_filter = self.payload["low_filter"]
            pipe.lowFilter = to_timestamp(low_filter) if low_filter is not None else 0
            
            pipe.limit = self.payload["limit"]
        else:
            raise ValueError("Unknown type for vertex query")

        return message

    @classmethod
    def edges(cls, keys):
        """
        Gets a set of edges. Generally this query is useful when you have a
        set of edges from a previous query upon which you want to construct a
        new query.

        `keys` represents the `EdgeKey`s that identifies the edges.
        """
        return cls("edges", keys=keys)

    def outbound_vertices(self, limit):
        """
        Get the vertices outbounding from the edges returned by this query.

        `limit` limits the number of returned vertices.
        """
        return VertexQuery("pipe", edge_query=self, converter="outbound", limit=limit)

    def inbound_vertices(self, limit):
        """
        Get the vertices inbounding from the edges returned by this query.

        `limit` limits the number of returned vertices.
        """
        return VertexQuery("pipe", edge_query=self, converter="inbound", limit=limit)

class BulkInsertItem(Enum):
    @classmethod
    def vertex(cls, vertex):
        return cls("vertex", vertex=vertex)

    @classmethod
    def edge(cls, key):
        return cls("edge", key=key)

    @classmethod
    def vertex_property(cls, id, name, value):
        return cls("vertex_property", id=id, name=name, value=value)

    @classmethod
    def edge_property(cls, key, name, value):
        return cls("edge_property", key=key, name=name, value=value)

    def to_message(self):
        message = indradb_capnp.BulkInsertItem.new_message()

        if self.type == "vertex":
            container = message.init("vertex")
            container.vertex = self.payload["vertex"].to_message()
        elif self.type == "edge":
            container = message.init("edge")
            container.key = self.payload["key"].to_message()
        elif self.type == "vertex_property":
            container = message.init("vertexProperty")
            container.id = self.payload["id"].bytes
            container.name = self.payload["name"]
            container.value = json.dumps(self.payload["value"])
        elif self.type == "edge_property":
            container = message.init("edgeProperty")
            container.key = self.payload["key"].to_message()
            container.name = self.payload["name"]
            container.value = json.dumps(self.payload["value"])
        else:
            raise ValueError("Unknown type for vertex query")

        return message
