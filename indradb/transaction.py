class Transaction(object):
    """
    A transaction. This class uses the builder pattern, so that you can easily
    chain queries together, e.g.:
    
    >>> Transaction().create_edge(...).get_vertices(...)
    """

    def __init__(self):
        self.payload = []

    def _add(self, **kwargs):
        self.payload.append(kwargs)

    def create_vertex(self, type):
        """
        Creates a new vertex.

        `type` specifies the vertex type. Must be less than 256 characters long, and can only contain letters, numbers,
        dashes, and underscores.
        """
        self._add(action="create_vertex", type=type)
        return self

    def get_vertices(self, query):
        """
        Gets vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        self._add(action="get_vertices", query=query.to_dict())
        return self

    def delete_vertices(self, query):
        """
        Deletes vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        self._add(action="delete_vertices", query=query.to_dict())
        return self

    def create_edge(self, key, weight):
        """
        Creates a new edge.

        `key` is the `EdgeKey` that identifies the edge. `weight` is the weight to set the edge to; it must be between
        -1.0 and 1.0.
        """
        self._add(action="create_edge", key=key.to_dict(), weight=weight)
        return self

    def get_edges(self, query):
        """
        Gets edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add(action="get_edges", query=query.to_dict())
        return self

    def get_edge_count(self, query):
        """
        Gets the number of edges that match a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add(action="get_edge_count", query=query.to_dict())
        return self

    def delete_edges(self, query):
        """
        Deletes edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add(action="delete_edges", query=query.to_dict())
        return self
