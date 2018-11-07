from .models import Vertex, Edge, VertexProperty, EdgeProperty
import uuid
import json

class Transaction(object):
    def __init__(self, trans):
        self.trans = trans

    def create_vertex(self, vertex):
        """
        Creates a new vertex.

        `vertex` specifies the `Vertex` to create.
        """
        deserialize = lambda message: message.result
        return self.trans.createVertex(vertex.to_message()).then(deserialize)

    def create_vertex_from_type(self, type):
        """
        Creates a new vertex from a type.

        `type` specifies the new vertex's type.
        """

        deserialize = lambda message: uuid.UUID(bytes=message.result)
        return self.trans.createVertexFromType(type).then(deserialize)

    def get_vertices(self, query):
        """
        Gets vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        deserialize = lambda message: [Vertex.from_message(v) for v in message.result]
        return self.trans.getVertices(query.to_message()).then(deserialize)

    def delete_vertices(self, query):
        """
        Deletes vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        deserialize = lambda message: message.result
        return self.trans.deleteVertices(query.to_message()).then(deserialize)

    def get_vertex_count(self):
        """
        Gets the total number of vertices in the datastore.
        """
        deserialize = lambda message: message.result
        return self.trans.getVertexCount().then(deserialize)

    def create_edge(self, key):
        """
        Creates a new edge.

        `key` is the `EdgeKey` that identifies the edge.
        """
        deserialize = lambda message: message.result
        return self.trans.createEdge(key.to_message()).then(deserialize)

    def get_edges(self, query):
        """
        Gets edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        deserialize = lambda message: [Edge.from_message(e) for e in message.result]
        return self.trans.getEdges(query.to_message()).then(deserialize)

    def delete_edges(self, query):
        """
        Deletes edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        deserialize = lambda message: message.result
        return self.trans.deleteEdges(query.to_message()).then(deserialize)

    def get_edge_count(self, id, t, direction):
        """
        Gets the number of edges related to a vertex.

        `id` specifies the ID of the vertex. `t` specifies which
        type of edges to count - set this to `None` if all edges should be
        counted. `direction` specifies the direction of edges to count -
        either `outbound` or `inbound`.
        """
        deserialize = lambda message: message.result
        return self.trans.getEdgeCount(id.bytes, t or "", direction).then(deserialize)

    def get_vertex_properties(self, query):
        """
        Gets vertex properties.

        `query` specifies the vertex properties query to run.
        """
        deserialize = lambda message: [VertexProperty.from_message(m) for m in message.result]
        return self.trans.getVertexProperties(query.to_message()).then(deserialize)

    def set_vertex_properties(self, query, value):
        """
        Sets vertex properties.

        `query` specifies the edge query to run. `value` specifies the value
        to set; it must be JSONable (i.e., it should be possible to pass
        `value` into `json.dumps`.)
        """
        deserialize = lambda message: message.result
        return self.trans.setVertexProperties(query.to_message(), json.dumps(value)).then(deserialize)

    def delete_vertex_properties(self, query):
        """
        Deletes vertex properties.

        `query` specifies the vertex query to run.
        """
        deserialize = lambda message: message.result
        return self.trans.deleteVertexProperties(query.to_message()).then(deserialize)

    def get_edge_properties(self, query):
        """
        Gets edge properties.

        `query` specifies the edge query to run.
        """
        deserialize = lambda message: [EdgeProperty.from_message(m) for m in message.result]
        return self.trans.getEdgeProperties(query.to_message()).then(deserialize)

    def set_edge_properties(self, query, value):
        """
        Sets edge properties.

        `query` specifies the edge query to run. `value` specifies the value
        to set; it must be JSONable (i.e., it should be possible to pass
        `value` into `json.dumps`.)
        """
        deserialize = lambda message: message.result
        return self.trans.setEdgeProperties(query.to_message(), json.dumps(value)).then(deserialize)

    def delete_edge_properties(self, query):
        """
        Deletes global properties.

        `query` specifies the edge query to run.
        """
        deserialize = lambda message: message.result
        return self.trans.deleteEdgeProperties(query.to_message()).then(deserialize)
