import iso8601

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
    An edge, which represents a relationship between things, and have types, weights, and when they were last updated.
    """

    def __init__(self, key, weight, update_datetime):
        """
        Creates a new edge.

        `key` is the `EdgeKey` to the edge. `weight` is the weight of the edge. `update_datetime` is when the edge's
        weight was last updated.
        """

        self.key = key
        self.weight = weight
        self.update_datetime = update_datetime

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        if self.key != other.key:
            return False
        if self.weight != other.weight:
            return False
        if self.update_datetime != other.update_datetime:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self):
        return dict(key=self.key.to_dict(), weight=self.weight, update_datetime=self.update_datetime.isoformat())

    @classmethod
    def from_dict(cls, d):
        """Converts a dict to an `Edge`. Useful for JSON deserialization."""
        return cls(
            key=EdgeKey.from_dict(d["key"]),
            weight=d["weight"],
            update_datetime=iso8601.parse_date(d["update_datetime"]),
        )

class VertexQuery(object):
    """A query for vertices."""

    def __init__(self, query):
        """
        Creates a new vertex query. Generally you shouldn't construct `VertexQuery` objects directly, but rather use
        the class methods.
        """
        self._query = query

    def __eq__(self, other):
        if not isinstance(other, VertexQuery):
            return False
        if self._query != other._query:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def all(cls, from_id, limit=DEFAULT_LIMIT):
        """
        Gets all vertices, filtered only the input arguments. Generally this query is useful when you want to iterate
        over all of the vertices in the datastore - e.g. to build an in-memory representation of the data.

        `from_id` represents the vertex UUID from which to start for the returned range (exclusive.) `limit` sets the
        limit of the number vertices to return.
        """
        return cls(dict(all=(from_id, limit)))

    @classmethod
    def vertex(cls, id):
        """
        Gets a single vertex.

        `id` represents the vertex UUID to get.
        """
        return cls(dict(vertex=id))

    @classmethod
    def vertices(cls, ids):
        """
        Gets a set of vertices. Generally this query is useful when you have a set of vertices from a previous query
        upon which you want to construct a new query.

        `ids` is the set of vertex UUIDs to get.
        """
        return cls(dict(vertices=ids))

    @classmethod
    def _pipe(cls, query, query_type_converter, limit=DEFAULT_LIMIT):
        """
        Creates a vertex query off of an edge query.

        `query` is the `EdgeQuery`. `query_type_converter` is a string - either `outbound` or `inbound` - specifying
        which end of vertices to get from the edges returned by the query. `limit` limits the number of vertices.
        """
        return cls(dict(pipe=(query, query_type_converter, limit)))

    def outbound_edges(self, type=None, high=None, low=None, limit=DEFAULT_LIMIT):
        """
        Get the edges outbounding from the vertices returned by this query.

        `type` optionally filters those edges to only have a specific type. `high` optionally filters those edges to
        only get ones updated at or before the given datetime. `low` optionally filters those edges to only get ones
        updated at or after the given datetime. `limit` limits the number of returned edges.
        """
        return EdgeQuery._pipe(
            self._query,
            "outbound",
            type=type,
            high=high.isoformat() if high else None,
            low=low.isoformat() if low else None,
            limit=limit
        )

    def inbound_edges(self, type=None, high=None, low=None, limit=DEFAULT_LIMIT):
        """
        Get the edges inbounding from the vertices returned by this query.

        `type` optionally filters those edges to only have a specific type. `high` optionally filters those edges to
        only get ones updated at or before the given datetime. `low` optionally filters those edges to only get ones
        updated at or after the given datetime. `limit` limits the number of returned edges.
        """
        return EdgeQuery._pipe(
            self._query,
            "inbound",
            type=type,
            high=high.isoformat() if high else None,
            low=low.isoformat() if low else None,
            limit=limit
        )

class EdgeQuery(object):
    """A query for edges."""

    def __init__(self, query):
        """
        Creates a new edge query. Generally you shouldn't construct `EdgeQuery` objects directly, but rather use the
        class methods.
        """
        self._query = query

    def __eq__(self, other):
        if not isinstance(other, VertexQuery):
            return False
        if self._query != other._query:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def edge(cls, key):
        """
        Gets a single edge.

        `key` represents the `EdgeKey` that identifies the edge.
        """
        return cls(dict(edge=key.to_dict()))

    @classmethod
    def edges(cls, keys):
        """
        Gets a set of edges. Generally this query is useful when you have a set of edges from a previous query upon
        which you want to construct a new query.

        `keys` represents the `EdgeKey`s that identifies the edges.
        """
        return cls(dict(edges=[key.to_dict() for key in keys]))

    @classmethod
    def _pipe(cls, query, query_type_converter, type=None, high=None, low=None, limit=DEFAULT_LIMIT):
        """
        Creates an edge query off of a vertex query.

        `query` is the `VertexQuery`. `query_type_converter` is a string - either `outbound` or `inbound` - specifying
        which end of edges to get from the vertices returned by the query. `type` optionally filters those edges to
        only have a specific type. `high` optionally filters those edges to only get ones updated at or before the
        given datetime. `low` optionally filters those edges to only get ones updated at or after the given datetime.
        `limit` limits the number of returned edges.
        """
        return cls(dict(pipe=(query, query_type_converter, type, high, low, limit)))

    def outbound_vertices(self, limit=DEFAULT_LIMIT):
        """
        Get the vertices outbounding from the edges returned by this query.

        `limit` limits the number of returned vertices.
        """
        return VertexQuery._pipe(self._query, "outbound", limit=limit)

    def inbound_vertices(self, limit=DEFAULT_LIMIT):
        """
        Get the vertices inbounding from the edges returned by this query.

        `limit` limits the number of returned vertices.
        """
        return VertexQuery._pipe(self._query, "inbound", limit=limit)
