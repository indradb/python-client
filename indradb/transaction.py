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

    def create_edge(self, key):
        """
        Creates a new edge.

        `key` is the `EdgeKey` that identifies the edge.
        -1.0 and 1.0.
        """
        self._add(action="create_edge", key=key.to_dict())
        return self

    def get_edges(self, query):
        """
        Gets edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add(action="get_edges", query=query.to_dict())
        return self

    def delete_edges(self, query):
        """
        Deletes edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add(action="delete_edges", query=query.to_dict())
        return self

    def get_edge_count(self, id, type_filter, direction):
        """
        Gets the number of edges related to a vertex.

        `id` specifies the ID of the vertex. `type_filter` specifies which
        type of edges to count - set this to `None` if all edges should be
        counted. `direction` specifies the direction of edges to count -
        either `outbound` or `inbound`.
        """
        self._add(action="get_edge_count", id=id, type_filter=type_filter, direction=direction)
        return self

    def get_global_metadata(self, name):
        """
        Gets global metadata.

        `name` specifies name of the global metadata to get.
        """
        self._add(action="get_global_metadata", name=name)
        return self

    def set_global_metadata(self, name, value):
        """
        Sets global metadata.

        `name` specifies name of the global metadata to get. `value` specifies
        the value to set.
        """
        self._add(action="set_global_metadata", name=name, value=value)
        return self

    def delete_global_metadata(self, name):
        """
        Deletes global metadata.

        `name` specifies name of the global metadata to delete.
        """
        self._add(action="delete_global_metadata", name=name)
        return self

    def get_vertex_metadata(self, query, name):
        """
        Gets vertex metadata.

        `query` specifies the vertex query to run. `name` specifies name of
        the metadata to get.
        """
        self._add(action="get_vertex_metadata", query=query.to_dict(), name=name)
        return self

    def set_vertex_metadata(self, query, name, value):
        """
        Sets vertex metadata.

        `query` specifies the edge query to run. `name` specifies name of the
        metadata to get. `value` specifies the value to set.
        """
        self._add(action="set_vertex_metadata", query=query.to_dict(), name=name, value=value)
        return self

    def delete_vertex_metadata(self, query, name):
        """
        Deletes vertex metadata.

        `query` specifies the vertex query to run. `name` specifies name of
        the metadata to delete.
        """
        self._add(action="delete_vertex_metadata", query=query.to_dict(), name=name)
        return self

    def get_edge_metadata(self, query, name):
        """
        Gets edge metadata.

        `query` specifies the edge query to run. `name` specifies name of the
        metadata to get.
        """
        self._add(action="get_edge_metadata", query=query.to_dict(), name=name)
        return self

    def set_edge_metadata(self, query, name, value):
        """
        Sets edge metadata.

        `query` specifies the edge query to run. `name` specifies name of the
        metadata to get. `value` specifies the value to set.
        """
        self._add(action="set_edge_metadata", query=query.to_dict(), name=name, value=value)
        return self

    def delete_edge_metadata(self, query, name):
        """
        Deletes global metadata.

        `query` specifies the edge query to run. `name` specifies name of the
        metadata to delete.
        """
        self._add(action="delete_edge_metadata", query=query.to_dict(), name=name)
        return self
