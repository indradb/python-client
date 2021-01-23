# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import indradb.indradb_pb2 as indradb__pb2


class IndraDBStub(object):
  # missing associated documentation comment in .proto file
  pass

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
    self.BulkInsert = channel.stream_unary(
        '/indradb.IndraDB/BulkInsert',
        request_serializer=indradb__pb2.BulkInsertItem.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.Transaction = channel.stream_stream(
        '/indradb.IndraDB/Transaction',
        request_serializer=indradb__pb2.TransactionRequest.SerializeToString,
        response_deserializer=indradb__pb2.TransactionResponse.FromString,
        )


class IndraDBServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Ping(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def BulkInsert(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Transaction(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
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
      'BulkInsert': grpc.stream_unary_rpc_method_handler(
          servicer.BulkInsert,
          request_deserializer=indradb__pb2.BulkInsertItem.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'Transaction': grpc.stream_stream_rpc_method_handler(
          servicer.Transaction,
          request_deserializer=indradb__pb2.TransactionRequest.FromString,
          response_serializer=indradb__pb2.TransactionResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'indradb.IndraDB', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))