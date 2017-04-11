class Transaction(object):
    """
    A transaction.
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

    def get_vertices(self, query):
        """
        Gets vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        self._add(action="get_vertices", query=query._query)

    def set_vertices(self, query, weight):
        """
        Updates existing vertices by a given query with a new type.

        `query` specifies the `VertexQuery` to use. `type` specifies the new type for the vertices; it must be less
        than 256 characters long, and can only contain letters, numbers,
        dashes, and underscores.
        """
        self._add(action="set_vertices", query=query._query, weight=weight)

    def delete_vertices(self, query):
        """
        Deletes vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        self._add(action="delete_vertices", query=query._query)

    def create_edge(self, key, weight):
        """
        Creates a new edge.

        `key` is the `EdgeKey` that identifies the edge. `weight` is the weight to set the edge to; it must be between
        -1.0 and 1.0.
        """
        key_dict = dict(outbound_id=key.outbound_id, type=key.type, inbound_id=key.inbound_id)
        self._add(action="create_edge", key=key_dict, weight=weight)

    def get_edges(self, query):
        """
        Gets edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add(action="get_edges", query=query._query)

    def get_edge_count(self, query):
        """
        Gets the number of edges that match a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add(action="get_edge_count", query=query._query)

    def set_edges(self, query, weight):
        """
        Updates existing edges that match a given query with a new weight.

        `query` specifies the `EdgeQuery` to use. `weight` is the weight to set the edges to; it must be between -1.0
        and 1.0.
        """
        self._add(action="set_edges", query=query._query, weight=weight)

    def delete_edges(self, query):
        """
        Deletes edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add(action="delete_edges", query=query._query)

    def run_script(self, name, payload):
        """
        Executes a lua script.

        `name` specifies the name of the lua script, which should be in the server's script root directory. It should
        include the `.lua` extension of the file. `payload` is a JSON-serializable payload to send to the script.
        """
        self._add(action="run_script", name=name, payload=payload)
