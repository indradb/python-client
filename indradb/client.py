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
        self.stub.Ping(req)

    def sync(self):
        req = proto.google_dot_protobuf_dot_empty__pb2.Empty()
        self.stub.Sync(req)

    def create_vertex(self, vertex):
        """
        Creates a new vertex.

        `vertex` specifies the `Vertex` to create.
        """
        req = vertex.to_message()
        res = self.stub.CreateVertex(req)
        return res.created

    def create_vertex_from_type(self, t):
        """
        Creates a new vertex from a type.

        `t` specifies the new vertex's type.
        """
        req = proto.Identifier(value=t)
        res = self.stub.CreateVertexFromType(req)
        return uuid.UUID(bytes=res.value)

    def create_edge(self, edge):
        """Creates a new edge."""
        req = edge.to_message()
        res = self.stub.CreateEdge(req)
        return res.created

    def get(self, query):
        """Gets values specified by a query."""
        req = query.to_message()
        res = self.stub.Get(req)
        for res_chunk in res:
            variant = res_chunk.WhichOneof("value")
            if variant == "count":
                yield res_chunk.count
            elif variant == "vertices":
                yield [Vertex.from_message(item) for item in res_chunk.vertices.vertices]
            elif variant == "edges":
                yield [Edge.from_message(item) for item in res_chunk.edges.edges]
            elif variant == "vertex_properties":
                yield [VertexProperties.from_message(item) for item in res_chunk.vertex_properties.vertex_properties]
            elif variant == "edge_properties":
                yield [EdgeProperties.from_message(item) for item in res_chunk.edge_properties.edge_properties]

    def delete(self, query):
        """Deletes values specified by a query."""
        req = query.to_message()
        self.stub.Delete(req)

    def set_properties(self, query, name, value):
        """Sets properties."""
        req = proto.SetPropertiesRequest(
            q=query.to_message(),
            name=proto.Identifier(value=name),
            value=proto.Json(value=json.dumps(value)),
        )

        self.stub.SetProperties(req)

    def index_property(self, name):
        req = proto.IndexPropertyRequest(name=proto.Identifier(value=name))
        return self.stub.IndexProperty(req)

    def execute_plugin(self, name, arg):
        req = proto.ExecutePluginRequest(
            name=proto.Identifier(value=name),
            arg=proto.Json(value=json.dumps(arg)),
        )
        res = self.stub.IndexProperty(req)
        return json.loads(res.value.value)

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

    def edge_property(self, edge, name, value):
        self._add_req(edge_property=proto.EdgePropertyBulkInsertItem(
            edge=edge.to_message(),
            name=proto.Identifier(value=name),
            value=proto.Json(value=json.dumps(value)),
        ))
        return self

    def execute(self, client):
        client.stub.BulkInsert(iter(self._reqs))
