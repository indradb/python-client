import json
import itertools
from .transaction import Transaction
from .hook import get_schema

capnp, indradb_capnp = get_schema()

class Client(object):
    """Represents a connection to IndraDB"""

    def __init__(self, host):
        """
        Creates a new client.

        `host` is a string that specifies the server location, in the format
        `hostname:port`.

        The optional `request_timeout` sets how many seconds to wait before a
        request times out (defaults to 60 seconds.)
        """

        self.host = host
        self.client = capnp.TwoPartyClient(self.host)
        self.service = self.client.bootstrap().cast_as(indradb_capnp.Service)

    def ping(self):
        return self.service.ping()

    def transaction(self):
        trans = self.service.transaction().wait()
        return Transaction(trans.transaction)

    def bulk_insert(self, outbound_vertex_type, inbound_vertex_type, edge_keys):
        request = self.service.bulkInsert_request()
        request.outboundVertexT = outbound_vertex_type
        request.inboundVertexT = inbound_vertex_type
        container = request.init("edgeKeys", len(edge_keys))

        for i, edge_key in enumerate(edge_keys):
            container[i] = edge_key.to_message()

        deserialize = lambda message: message.result
        return request.send().then(deserialize)
