import json
import itertools
from .transaction import Transaction
from .hook import get_schema

capnp, indradb_capnp = get_schema()

def bulk_insert_request(request, items):
    serialized = request.init("items", len(items))

    for i, (value, properties) in enumerate(items):
        serialized[i].value = value.to_message()
        properties_builder = serialized[i].init("properties", len(properties))

        for i, prop in enumerate(properties):
            properties_builder[i] = prop.to_message()

    deserialize = lambda message: message.result
    return request.send().then(deserialize)


class Client(object):
    """Represents a connection to IndraDB"""

    def __init__(self, host):
        """
        Creates a new client.

        `host` is a string that specifies the server location, in the format
        `hostname:port`.

        The optional `request_timeout` sets how many seconds to wait before a request times out (defaults to 60
        seconds.)
        """

        self.host = host
        self.client = capnp.TwoPartyClient(self.host)
        self.service = self.client.bootstrap().cast_as(indradb_capnp.Service)

    def ping(self):
        return self.service.ping()

    def transaction(self):
        trans = self.service.transaction().wait()
        return Transaction(trans.transaction)

    def bulk_insert_vertices(self, items):
        return bulk_insert_request(self.service.bulkInsertVertices_request(), items)

    def bulk_insert_edges(self, items):
        return bulk_insert_request(self.service.bulkInsertEdges_request(), items)
