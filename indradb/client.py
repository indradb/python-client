import uuid
import json
import itertools

import grpc
import indradb.indradb_pb2 as indradb_proto
import indradb.indradb_pb2_grpc as indradb_grpc

from .models import Vertex, Edge, VertexProperty, EdgeProperty, VertexProperties, EdgeProperties
from indradb import proto

TRANSACTION_STREAMING_TYPES = [
    "get_vertices",
    "get_edges",
    "get_vertex_properties",
    "get_all_vertex_properties",
    "get_edge_properties",
    "get_all_edge_properties",
]

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
        req = indradb_proto.google_dot_protobuf_dot_empty__pb2.Empty()
        return self.stub.Ping(req)

    def create_vertex(self, vertex):
        """
        Creates a new vertex.

        `vertex` specifies the `Vertex` to create.
        """
        return next(Transaction().create_vertex(vertex).execute(self))

    def create_vertex_from_type(self, type):
        """
        Creates a new vertex from a type.

        `type` specifies the new vertex's type.
        """
        return next(Transaction().create_vertex_from_type(type).execute(self))

    def get_vertices(self, query):
        """
        Gets vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        return next(Transaction().get_vertices(query).execute(self))

    def delete_vertices(self, query):
        """
        Deletes vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        return next(Transaction().delete_vertices(query).execute(self))

    def get_vertex_count(self):
        """
        Gets the total number of vertices in the datastore.
        """
        return next(Transaction().get_vertex_count().execute(self))

    def create_edge(self, key):
        """
        Creates a new edge.

        `key` is the `EdgeKey` that identifies the edge.
        """
        return next(Transaction().create_edge(key).execute(self))

    def get_edges(self, query):
        """
        Gets edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        return next(Transaction().get_edges(query).execute(self))

    def delete_edges(self, query):
        """
        Deletes edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        return next(Transaction().delete_edges(query).execute(self))

    def get_edge_count(self, id, t, direction):
        """
        Gets the number of edges related to a vertex.

        `id` specifies the ID of the vertex. `t` specifies which
        type of edges to count - set this to `None` if all edges should be
        counted. `direction` specifies the direction of edges to count.
        """
        return next(Transaction().get_edge_count(id, t, direction).execute(self))

    def get_vertex_properties(self, query):
        """
        Gets vertex properties.

        `query` specifies the vertex properties query to run.
        """
        return next(Transaction().get_vertex_properties(query).execute(self))

    def set_vertex_properties(self, query, value):
        """
        Sets vertex properties.

        `query` specifies the edge query to run. `value` specifies the value
        to set; it must be JSONable (i.e., it should be possible to pass
        `value` into `json.dumps`.)
        """
        return next(Transaction().set_vertex_properties(query, value).execute(self))

    def delete_vertex_properties(self, query):
        """
        Deletes vertex properties.

        `query` specifies the vertex query to run.
        """
        return next(Transaction().delete_vertex_properties(query).execute(self))

    def get_edge_properties(self, query):
        """
        Gets edge properties.

        `query` specifies the edge query to run.
        """
        return next(Transaction().get_edge_properties(query).execute(self))

    def set_edge_properties(self, query, value):
        """
        Sets edge properties.

        `query` specifies the edge query to run. `value` specifies the value
        to set; it must be JSONable (i.e., it should be possible to pass
        `value` into `json.dumps`.)
        """
        return next(Transaction().set_edge_properties(query, value).execute(self))

    def delete_edge_properties(self, query):
        """
        Deletes global properties.

        `query` specifies the edge query to run.
        """
        return next(Transaction().delete_edge_properties(query).execute(self))

    def get_all_vertex_properties(self, query):
        """
        Get all properties associated with the vertices from `query.`

        `query` specifies the vertex query to run.
        """
        return next(Transaction().get_all_vertex_properties(query).execute(self))

    def get_all_edge_properties(self, query):
        """
        Get all properties associated with the edges from `query.`

        `query` specifies the edge query to run.
        """
        return next(Transaction().get_all_edge_properties(query).execute(self))

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
            name=name,
            value=proto.Json(value=json.dumps(value)),
        ))
        return self

    def edge_property(self, key, name, value):
        self._add_req(edge_property=proto.EdgePropertyBulkInsertItem(
            key=key.to_message(),
            name=name,
            value=proto.Json(value=json.dumps(value)),
        ))
        return self

    def execute(self, client):
        client.stub.BulkInsert(iter(self._reqs))

class Transaction:
    def __init__(self):
        self._next_request_id = 1
        self._reqs = []

    def _add_req(self, **kwargs):
        self._reqs.append(proto.TransactionRequest(request_id=self._next_request_id, **kwargs))
        self._next_request_id += 1

    def create_vertex(self, vertex):
        """
        Creates a new vertex.

        `vertex` specifies the `Vertex` to create.
        """
        self._add_req(create_vertex=vertex.to_message())
        return self

    def create_vertex_from_type(self, type):
        """
        Creates a new vertex from a type.

        `type` specifies the new vertex's type.
        """
        self._add_req(create_vertex_from_type=proto.Type(value=type))
        return self

    def get_vertices(self, query):
        """
        Gets vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        self._add_req(get_vertices=query.to_message())
        return self

    def delete_vertices(self, query):
        """
        Deletes vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        self._add_req(delete_vertices=query.to_message())
        return self

    def get_vertex_count(self):
        """
        Gets the total number of vertices in the datastore.
        """
        self._add_req(get_vertex_count=indradb_proto.google_dot_protobuf_dot_empty__pb2.Empty())
        return self

    def create_edge(self, key):
        """
        Creates a new edge.

        `key` is the `EdgeKey` that identifies the edge.
        """
        self._add_req(create_edge=key.to_message())
        return self

    def get_edges(self, query):
        """
        Gets edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add_req(get_edges=query.to_message())
        return self

    def delete_edges(self, query):
        """
        Deletes edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        self._add_req(delete_edges=query.to_message())
        return self

    def get_edge_count(self, id, t, direction):
        """
        Gets the number of edges related to a vertex.

        `id` specifies the ID of the vertex. `t` specifies which
        type of edges to count - set this to `None` if all edges should be
        counted. `direction` specifies the direction of edges to count.
        """
        self._add_req(get_edge_count=proto.GetEdgeCountRequest(
            id=proto.Uuid(value=id.bytes),
            t=proto.Type(value=t) if t is not None else None,
            direction=direction.value,
        ))
        return self

    def get_vertex_properties(self, query):
        """
        Gets vertex properties.

        `query` specifies the vertex properties query to run.
        """
        self._add_req(get_vertex_properties=query.to_message())
        return self

    def set_vertex_properties(self, query, value):
        """
        Sets vertex properties.

        `query` specifies the edge query to run. `value` specifies the value
        to set; it must be JSONable (i.e., it should be possible to pass
        `value` into `json.dumps`.)
        """
        self._add_req(set_vertex_properties=proto.SetVertexPropertiesRequest(
            q=query.to_message(),
            value=proto.Json(value=json.dumps(value)),
        ))
        return self

    def delete_vertex_properties(self, query):
        """
        Deletes vertex properties.

        `query` specifies the vertex query to run.
        """
        self._add_req(delete_vertex_properties=query.to_message())
        return self

    def get_edge_properties(self, query):
        """
        Gets edge properties.

        `query` specifies the edge query to run.
        """
        self._add_req(get_edge_properties=query.to_message())
        return self

    def set_edge_properties(self, query, value):
        """
        Sets edge properties.

        `query` specifies the edge query to run. `value` specifies the value
        to set; it must be JSONable (i.e., it should be possible to pass
        `value` into `json.dumps`.)
        """
        self._add_req(set_edge_properties=proto.SetEdgePropertiesRequest(
            q=query.to_message(),
            value=proto.Json(value=json.dumps(value)),
        ))
        return self

    def delete_edge_properties(self, query):
        """
        Deletes global properties.

        `query` specifies the edge query to run.
        """
        self._add_req(delete_edge_properties=query.to_message())
        return self

    def get_all_vertex_properties(self, query):
        """
        Get all properties associated with the vertices from `query.`

        `query` specifies the vertex query to run.
        """
        self._add_req(get_all_vertex_properties=query.to_message())
        return self

    def get_all_edge_properties(self, query):
        """
        Get all properties associated with the edges from `query.`

        `query` specifies the edge query to run.
        """
        self._add_req(get_all_edge_properties=query.to_message())
        return self

    def execute(self, client):
        responses = client.stub.Transaction(iter(self._reqs))
        for req in self._reqs:
            req_variant = req.WhichOneof("request")
            if req_variant in TRANSACTION_STREAMING_TYPES:
                buf = []
                for res in responses:
                    if res.HasField("empty"):
                        break
                    buf.append(_parse_transaction_response(res))
                yield buf
            else:
                yield _parse_transaction_response(next(responses))

def _parse_transaction_response(res):
    res_variant = res.WhichOneof("response")
    if res_variant == "empty":
        return None
    elif res_variant == "ok":
        return res.ok
    elif res_variant == "count":
        return res.count
    elif res_variant == "id":
        return uuid.UUID(bytes=res.id.value)
    elif res_variant == "vertex":
        return Vertex.from_message(res.vertex)
    elif res_variant == "edge":
        return Edge.from_message(res.edge)
    elif res_variant == "vertex_property":
        return VertexProperty.from_message(res.vertex_property)
    elif res_variant == "vertex_properties":
        return VertexProperties.from_message(res.vertex_properties)
    elif res_variant == "edge_property":
        return EdgeProperty.from_message(res.edge_property)
    elif res_variant == "edge_properties":
        return EdgeProperties.from_message(res.edge_properties)
