import uuid
import json
import itertools

import grpc
import indradb.indradb_pb2_grpc as indradb_grpc

from .models import Vertex, Edge, VertexProperty, EdgeProperty, VertexProperties, EdgeProperties
from indradb import proto

class Client:
    """Represents a connection to IndraDB"""

    def __init__(self, host="localhost:27615"):
        """
        Creates a new client.

        `host` is a string that specifies the server location, in the format
        `hostname:port`.
        """

        self.host = host
        channel = grpc.insecure_channel(host)
        self.stub = indradb_grpc.IndraDBStub(channel)

    def ping(self):
        req = proto.google_dot_protobuf_dot_empty__pb2.Empty()
        return self.stub.Ping(req)

    def index_property(self, name):
        req = proto.IndexPropertyRequest(name=proto.Identifier(value=name))
        return self.stub.IndexProperty(req)

    def create_vertex(self, vertex):
        """
        Creates a new vertex.

        `vertex` specifies the `Vertex` to create.
        """
        req = vertex.to_message()
        return self.stub.CreateVertex(req).created

    def create_vertex_from_type(self, t):
        """
        Creates a new vertex from a type.

        `t` specifies the new vertex's type.
        """
        req = proto.Identifier(value=t)
        res = self.stub.CreateVertexFromType(req)
        return uuid.UUID(bytes=res.value)

    def get_vertices(self, query):
        """
        Gets vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        req = query.to_message()
        for res in self.stub.GetVertices(req):
            yield Vertex.from_message(res)

    def delete_vertices(self, query):
        """
        Deletes vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        req = query.to_message()
        self.stub.DeleteVertices(req)

    def get_vertex_count(self):
        """
        Gets the total number of vertices in the datastore.
        """
        req = proto.google_dot_protobuf_dot_empty__pb2.Empty()
        return self.stub.GetVertexCount(req).count

    def create_edge(self, key):
        """
        Creates a new edge.

        `key` is the `EdgeKey` that identifies the edge.
        """
        req = key.to_message()
        return self.stub.CreateEdge(req).created

    def get_edges(self, query):
        """
        Gets edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        req = query.to_message()
        for res in self.stub.GetEdges(req):
            yield Edge.from_message(res)

    def delete_edges(self, query):
        """
        Deletes edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        req = query.to_message()
        self.stub.DeleteEdges(req)

    def get_edge_count(self, id, t, direction):
        """
        Gets the number of edges related to a vertex.

        `id` specifies the ID of the vertex. `t` specifies which
        type of edges to count - set this to `None` if all edges should be
        counted. `direction` specifies the direction of edges to count.
        """
        req = proto.GetEdgeCountRequest(
            id=proto.Uuid(value=id.bytes),
            t=proto.Identifier(value=t) if t is not None else None,
            direction=direction.value,
        )
        return self.stub.GetEdgeCount(req).count

    def get_vertex_properties(self, query):
        """
        Gets vertex properties.

        `query` specifies the vertex properties query to run.
        """
        req = query.to_message()
        for res in self.stub.GetVertexProperties(req):
            yield VertexProperty.from_message(res)

    def set_vertex_properties(self, query, value):
        """
        Sets vertex properties.

        `query` specifies the edge query to run. `value` specifies the value
        to set; it must be JSONable (i.e., it should be possible to pass
        `value` into `json.dumps`.)
        """
        req = proto.SetVertexPropertiesRequest(
            q=query.to_message(),
            value=proto.Json(value=json.dumps(value)),
        )
        self.stub.SetVertexProperties(req)

    def delete_vertex_properties(self, query):
        """
        Deletes vertex properties.

        `query` specifies the vertex query to run.
        """
        req = query.to_message()
        self.stub.DeleteVertexProperties(req)

    def get_edge_properties(self, query):
        """
        Gets edge properties.

        `query` specifies the edge query to run.
        """
        req = query.to_message()
        for res in self.stub.GetEdgeProperties(req):
            yield EdgeProperty.from_message(res)

    def set_edge_properties(self, query, value):
        """
        Sets edge properties.

        `query` specifies the edge query to run. `value` specifies the value
        to set; it must be JSONable (i.e., it should be possible to pass
        `value` into `json.dumps`.)
        """
        req = proto.SetEdgePropertiesRequest(
            q=query.to_message(),
            value=proto.Json(value=json.dumps(value)),
        )
        self.stub.SetEdgeProperties(req)

    def delete_edge_properties(self, query):
        """
        Deletes global properties.

        `query` specifies the edge query to run.
        """
        req = query.to_message()
        self.stub.DeleteEdgeProperties(req)

    def get_all_vertex_properties(self, query):
        """
        Get all properties associated with the vertices from `query.`

        `query` specifies the vertex query to run.
        """
        req = query.to_message()
        for res in self.stub.GetAllVertexProperties(req):
            yield VertexProperties.from_message(res)

    def get_all_edge_properties(self, query):
        """
        Get all properties associated with the edges from `query.`

        `query` specifies the edge query to run.
        """
        req = query.to_message()
        for res in self.stub.GetAllEdgeProperties(req):
            yield EdgeProperties.from_message(res)

    def sync(self):
        """
        Syncs persisted content. Depending on the datastore implementation,
        this has different meanings - including potentially being a no-op.
        """
        req = proto.google_dot_protobuf_dot_empty__pb2.Empty()
        self.stub.Sync(req)

    def execute_plugin(self, name, arg):
        """
        Executes a plugin and returns back the response from the plugin.

        `name` specifies the plugin name to execute. `arg` specifies the
        argument to pass in; it must be JSONable (i.e., it should be possible
        to pass `arg` into `json.dumps`.)
        """
        req = proto.ExecutePluginRequest(
            name=name,
            arg=proto.Json(value=json.dumps(arg)) if arg is not None else None,
        )
        res = self.stub.ExecutePlugin(req)
        return json.loads(res.value)

class BulkInserter:
    def __init__(self):
        self._reqs = []

    def _add_req(self, **kwargs):
        self._reqs.append(proto.BulkInsertItem(**kwargs))

    def vertex(self, vertex):
        self._add_req(vertex=vertex.to_message())
        return self

    def edge(self, key):
        self._add_req(edge=key.to_message())
        return self

    def vertex_property(self, id, name, value):
        self._add_req(vertex_property=proto.VertexPropertyBulkInsertItem(
            id=proto.Uuid(value=id.bytes),
            name=proto.Identifier(value=name),
            value=proto.Json(value=json.dumps(value)),
        ))
        return self

    def edge_property(self, key, name, value):
        self._add_req(edge_property=proto.EdgePropertyBulkInsertItem(
            key=key.to_message(),
            name=proto.Identifier(value=name),
            value=proto.Json(value=json.dumps(value)),
        ))
        return self

    def execute(self, client):
        client.stub.BulkInsert(iter(self._reqs))
