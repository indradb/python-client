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

    def bulk_insert(self, items):
        request = self.service.bulkInsert_request()
        container = request.init("items", len(items))

        for i, item in enumerate(items):
            container[i] = item.to_message()

        deserialize = lambda message: message.result
        return request.send().then(deserialize)
