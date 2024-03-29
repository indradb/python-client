# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import indradb.indradb_pb2 as indradb__pb2


class IndraDBStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Ping = channel.unary_unary(
                '/indradb.IndraDB/Ping',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.Sync = channel.unary_unary(
                '/indradb.IndraDB/Sync',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.CreateVertex = channel.unary_unary(
                '/indradb.IndraDB/CreateVertex',
                request_serializer=indradb__pb2.Vertex.SerializeToString,
                response_deserializer=indradb__pb2.CreateResponse.FromString,
                )
        self.CreateVertexFromType = channel.unary_unary(
                '/indradb.IndraDB/CreateVertexFromType',
                request_serializer=indradb__pb2.Identifier.SerializeToString,
                response_deserializer=indradb__pb2.Uuid.FromString,
                )
        self.CreateEdge = channel.unary_unary(
                '/indradb.IndraDB/CreateEdge',
                request_serializer=indradb__pb2.Edge.SerializeToString,
                response_deserializer=indradb__pb2.CreateResponse.FromString,
                )
        self.Get = channel.unary_stream(
                '/indradb.IndraDB/Get',
                request_serializer=indradb__pb2.Query.SerializeToString,
                response_deserializer=indradb__pb2.QueryOutputValue.FromString,
                )
        self.Delete = channel.unary_unary(
                '/indradb.IndraDB/Delete',
                request_serializer=indradb__pb2.Query.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.SetProperties = channel.unary_unary(
                '/indradb.IndraDB/SetProperties',
                request_serializer=indradb__pb2.SetPropertiesRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.BulkInsert = channel.stream_unary(
                '/indradb.IndraDB/BulkInsert',
                request_serializer=indradb__pb2.BulkInsertItem.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.IndexProperty = channel.unary_unary(
                '/indradb.IndraDB/IndexProperty',
                request_serializer=indradb__pb2.IndexPropertyRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.ExecutePlugin = channel.unary_unary(
                '/indradb.IndraDB/ExecutePlugin',
                request_serializer=indradb__pb2.ExecutePluginRequest.SerializeToString,
                response_deserializer=indradb__pb2.ExecutePluginResponse.FromString,
                )


class IndraDBServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Ping(self, request, context):
        """Pings the server.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Sync(self, request, context):
        """Syncs persisted content. Depending on the datastore implementation,
        this has different meanings - including potentially being a no-op.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateVertex(self, request, context):
        """Creates a new vertex.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateVertexFromType(self, request, context):
        """Creates a new vertex with just a type specification. As opposed to
        `CreateVertex`, this is used when you do not want to manually specify
        the vertex's UUID. Returns the new vertex's UUID.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateEdge(self, request, context):
        """Creates a new edge.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """Gets values specified by a query.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Deletes values specified by a query.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetProperties(self, request, context):
        """Sets properties.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def BulkInsert(self, request_iterator, context):
        """Bulk inserts many vertices, edges, and/or properties.

        Note that datastores have discretion on how to approach safeguard vs
        performance tradeoffs. In particular:
        * If the datastore is disk-backed, it may or may not flush before
        returning.
        * The datastore might not verify for correctness; e.g., it might not
        ensure that the relevant vertices exist before inserting an edge.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def IndexProperty(self, request, context):
        """Enables indexing on a specified property. When indexing is enabled on a
        property, it's possible to query on its presence and values.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecutePlugin(self, request, context):
        """Executes a plugin and returns back the response from the plugin.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_IndraDBServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'Sync': grpc.unary_unary_rpc_method_handler(
                    servicer.Sync,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'CreateVertex': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateVertex,
                    request_deserializer=indradb__pb2.Vertex.FromString,
                    response_serializer=indradb__pb2.CreateResponse.SerializeToString,
            ),
            'CreateVertexFromType': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateVertexFromType,
                    request_deserializer=indradb__pb2.Identifier.FromString,
                    response_serializer=indradb__pb2.Uuid.SerializeToString,
            ),
            'CreateEdge': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateEdge,
                    request_deserializer=indradb__pb2.Edge.FromString,
                    response_serializer=indradb__pb2.CreateResponse.SerializeToString,
            ),
            'Get': grpc.unary_stream_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=indradb__pb2.Query.FromString,
                    response_serializer=indradb__pb2.QueryOutputValue.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=indradb__pb2.Query.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'SetProperties': grpc.unary_unary_rpc_method_handler(
                    servicer.SetProperties,
                    request_deserializer=indradb__pb2.SetPropertiesRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'BulkInsert': grpc.stream_unary_rpc_method_handler(
                    servicer.BulkInsert,
                    request_deserializer=indradb__pb2.BulkInsertItem.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'IndexProperty': grpc.unary_unary_rpc_method_handler(
                    servicer.IndexProperty,
                    request_deserializer=indradb__pb2.IndexPropertyRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'ExecutePlugin': grpc.unary_unary_rpc_method_handler(
                    servicer.ExecutePlugin,
                    request_deserializer=indradb__pb2.ExecutePluginRequest.FromString,
                    response_serializer=indradb__pb2.ExecutePluginResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'indradb.IndraDB', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class IndraDB(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/Ping',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Sync(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/Sync',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateVertex(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/CreateVertex',
            indradb__pb2.Vertex.SerializeToString,
            indradb__pb2.CreateResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateVertexFromType(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/CreateVertexFromType',
            indradb__pb2.Identifier.SerializeToString,
            indradb__pb2.Uuid.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateEdge(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/CreateEdge',
            indradb__pb2.Edge.SerializeToString,
            indradb__pb2.CreateResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/indradb.IndraDB/Get',
            indradb__pb2.Query.SerializeToString,
            indradb__pb2.QueryOutputValue.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/Delete',
            indradb__pb2.Query.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetProperties(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/SetProperties',
            indradb__pb2.SetPropertiesRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def BulkInsert(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/indradb.IndraDB/BulkInsert',
            indradb__pb2.BulkInsertItem.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def IndexProperty(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/IndexProperty',
            indradb__pb2.IndexPropertyRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ExecutePlugin(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/indradb.IndraDB/ExecutePlugin',
            indradb__pb2.ExecutePluginRequest.SerializeToString,
            indradb__pb2.ExecutePluginResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
