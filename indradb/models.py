import arrow

DEFAULT_LIMIT = 1000

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

    def to_dict(self):
        return dict(id=self.id, type=self.type)

    @classmethod
    def from_dict(cls, d):
        """
        Converts a dict to a `Vertex`. Useful for JSON deserialization.
        """
        return cls(id=d["id"], type=d["type"])

class EdgeKey(object):
    """Identifies an edge."""

    def __init__(self, outbound_id, type, inbound_id):
        """
        Creates a new edge key.
        
        `outbound_id` is the vertex UUID from which the edge is outbounding. `type` is the edge type. `inbound_id` is
        the vertex UUID into which the edge is inbounding.
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

    def to_dict(self):
        return dict(outbound_id=self.outbound_id, type=self.type, inbound_id=self.inbound_id)

    @classmethod
    def from_dict(cls, d):
        """Converts a dict to an `EdgeKey`. Useful for JSON deserialization."""
        return cls(
            outbound_id=d["outbound_id"],
            type=d["type"],
            inbound_id=d["inbound_id"]
        )

class Edge(object):
    """
    An edge, which represents a relationship between things, and have types and when they were last updated.
    """

    def __init__(self, key, created_datetime):
        """
        Creates a new edge.

        `key` is the `EdgeKey` to the edge. `created_datetime` is when the edge
        was created.
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

    def to_dict(self):
        return dict(key=self.key.to_dict(), created_datetime=self.created_datetime.isoformat())

    @classmethod
    def from_dict(cls, d):
        """Converts a dict to an `Edge`. Useful for JSON deserialization."""

        return cls(
            key=EdgeKey.from_dict(d["key"]),
            created_datetime=arrow.get(d["created_datetime"]),
        )

class VertexMetadata(object):
    """
    Metadata attached to a vertex
    """

    def __init__(self, id, value):
        """
        Creates a new vertex metadata.

        `id` is the vertex ID that the metadata is attached to. `value`
        represents the metadata value.
        """

        self.id = id
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, VertexMetadata):
            return False
        if self.id != other.id:
            return False
        if self.value != other.value:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_dict(cls, d):
        """Converts a dict to `VertexMetadata`. Useful for JSON deserialization."""

        return cls(
            id=d["id"],
            value=d["value"]
        )

class EdgeMetadata(object):
    """
    Metadata attached to an edge
    """

    def __init__(self, key, value):
        """
        Creates a new edge metadata.

        `key` is the edge key that the metadata is attached to. `value`
        represents the metadata value.
        """

        self.key = key
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, EdgeMetadata):
            return False
        if self.key != other.key:
            return False
        if self.value != other.value:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_dict(cls, d):
        """Converts a dict to `VertexMetadata`. Useful for JSON deserialization."""

        return cls(
            key=EdgeKey.from_dict(d["key"]),
            value=d["value"]
        )

class MapReducePing(object):
    """An update from a mapreduce call."""

    def __init__(self, finished, processing, sent):
        """
        Creates a new mapreduce ping.

        `finished` is how many mapreduce tasks have finished.
        `processing` is how many mapreduce tasks are currently being
        processed. `sent` is how many mapreduce tasks have been sent to be
        processed.
        """

        self.finished = finished
        self.processing = processing
        self.sent = sent

    @classmethod
    def from_dict(cls, d):
        """Converts a dict to `MapReducePing`. Useful for JSON deserialization."""

        return cls(
            finished=d["finished"],
            processing=d["processing"],
            sent=d["sent"]
        )
    
class Query(object):
    """Abstract class that represents a query"""

    def __init__(self, type, **kwargs):
        """
        Creates a new query. Generally you shouldn't construct a query objects directly, but rather use
        the class methods.
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

    def to_dict(self):
        return dict(type=self.type, **self.payload)

class VertexQuery(Query):
    """A query for vertices."""

    @classmethod
    def all(cls, start_id=None, limit=DEFAULT_LIMIT):
        """
        Gets all vertices, filtered only the input arguments. Generally this query is useful when you want to iterate
        over all of the vertices in the datastore - e.g. to build an in-memory representation of the data.

        `start_id` represents the vertex UUID from which to start for the returned range (exclusive.) `limit` sets the
        limit of the number vertices to return.
        """
        return cls("all", start_id=start_id, limit=limit)

    @classmethod
    def vertices(cls, ids):
        """
        Gets a set of vertices. Generally this query is useful when you have a set of vertices from a previous query
        upon which you want to construct a new query.

        `ids` is the set of vertex UUIDs to get.
        """
        return cls("vertices", ids=ids)

    def outbound_edges(self, type_filter=None, high_filter=None, low_filter=None, limit=DEFAULT_LIMIT):
        """
        Get the edges outbounding from the vertices returned by this query.

        `type_filter` optionally filters those edges to only have a specific type. `high_filter` optionally filters
        those edges to only get ones updated at or before the given datetime. `low_filter` optionally filters those
        edges to only get ones updated at or after the given datetime. `limit` limits the number of returned edges.
        """
        return EdgeQuery(
            "pipe",
            vertex_query=self.to_dict(),
            converter="outbound",
            type_filter=type_filter,
            high_filter=high_filter.isoformat() if high_filter else None,
            low_filter=low_filter.isoformat() if low_filter else None,
            limit=limit
        )

    def inbound_edges(self, type_filter=None, high_filter=None, low_filter=None, limit=DEFAULT_LIMIT):
        """
        Get the edges inbounding from the vertices returned by this query.

        `type_filter` optionally filters those edges to only have a specific type. `high_filter` optionally filters
        those edges to only get ones updated at or before the given datetime. `low_filter` optionally filters those
        edges to only get ones updated at or after the given datetime. `limit` limits the number of returned edges.
        """
        return EdgeQuery(
            "pipe",
            vertex_query=self.to_dict(),
            converter="inbound",
            type_filter=type_filter,
            high_filter=high_filter.isoformat() if high_filter else None,
            low_filter=low_filter.isoformat() if low_filter else None,
            limit=limit
        )

class EdgeQuery(Query):
    """A query for edges."""

    @classmethod
    def edges(cls, keys):
        """
        Gets a set of edges. Generally this query is useful when you have a set of edges from a previous query upon
        which you want to construct a new query.

        `keys` represents the `EdgeKey`s that identifies the edges.
        """
        return cls("edges", keys=[key.to_dict() for key in keys])

    def outbound_vertices(self, limit=DEFAULT_LIMIT):
        """
        Get the vertices outbounding from the edges returned by this query.

        `limit` limits the number of returned vertices.
        """
        return VertexQuery("pipe", edge_query=self.to_dict(), converter="outbound", limit=limit)

    def inbound_vertices(self, limit=DEFAULT_LIMIT):
        """
        Get the vertices inbounding from the edges returned by this query.

        `limit` limits the number of returned vertices.
        """
        return VertexQuery("pipe", edge_query=self.to_dict(), converter="inbound", limit=limit)
