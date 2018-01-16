import requests
import json
import itertools
from indradb.models import Vertex, Edge
from indradb.errors import Error

# Default time in seconds before a request times out
DEFAULT_REQUEST_TIMEOUT = 60

# Convenience function for building a path
_path = lambda *parts: "/%s" % "/".join(parts)

class Client(object):
    """Represents a connection to IndraDB"""

    def __init__(self, host, account_id, secret, request_timeout=DEFAULT_REQUEST_TIMEOUT, raise_on_error=True, scheme="https"):
        """
        Creates a new client.

        `host` specifies the hostname and port of the server, specified either as a tuple or a string of the format
        `hostname:port`.

        `account_id` and `secret` specify the authentication credentials of the
        account making the request.

        The optional `request_timeout` sets how many seconds to wait before a request times out (defaults to 60
        seconds.) The optional `raise_on_error` specifies whether to raise an error if a non-200 response is received.
        The optional `scheme` sets what protocol to use (`http` or `https`.) This defaults to `https`, but if your
        server does not accept https requests, you will get an error.
        """

        if isinstance(host, tuple):
            self.host = host
        else:
            parts = host.split(":")
            self.host = (parts[0], int(parts[1]))

        self.scheme = scheme
        self.account_id = account_id
        self.secret = secret
        self.request_timeout = request_timeout
        self.raise_on_error = raise_on_error
        self._session = requests.Session()

    def _request(self, method, endpoint, query_params=None, body=None):
        """Makes a request"""

        response = self._session.request(method, "%s://%s:%s%s" % (self.scheme, self.host[0], self.host[1], endpoint),
            params=query_params,
            data=json.dumps(body) if body else None,
            timeout=self.request_timeout,
            auth=(self.account_id, self.secret),
            headers={
                "content-type": "application/json"
            }
        )

        if self.raise_on_error and (response.status_code < 200 or response.status_code > 299):
            try:
                body = response.json()
            except Exception as e:
                body = None

            if isinstance(body, dict) and body.get("error") != None:
                raise Error(response.status_code, body.get("error"))
            else:
                raise Error(response.status_code, "Unexpected response code")

        return response.json()

    def create_vertex(self, type):
        """
        Creates a new vertex.

        `type` specifies the vertex type. Must be less than 256 characters long, and can only contain letters, numbers,
        dashes, and underscores.
        """
        query_params = dict(type=type)
        return self._request("POST", "/vertex", query_params)

    def get_vertices(self, query):
        """
        Gets vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        query_params = dict(q=json.dumps(query.to_dict()))
        response = self._request("GET", "/vertex", query_params=query_params)
        return [Vertex.from_dict(item) for item in response]

    def delete_vertices(self, query):
        """
        Deletes vertices by a given query.

        `query` specifies the `VertexQuery` to use.
        """
        query_params = dict(q=json.dumps(query.to_dict()))
        return self._request("DELETE", "/vertex", query_params=query_params)

    def create_edge(self, key, weight):
        """
        Creates a new edge.

        `key` is the `EdgeKey` that identifies the edge. `weight` is the weight to set the edge to; it must be between
        -1.0 and 1.0.
        """
        query_params = dict(weight=weight)
        return self._request("PUT", _path("edge", key.outbound_id, key.type, key.inbound_id), query_params=query_params)

    def get_edges(self, query):
        """
        Gets edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        query_params = dict(q=json.dumps(query.to_dict()))
        response = self._request("GET", "/edge", query_params=query_params)
        return [Edge.from_dict(item) for item in response]

    def get_edge_count(self, query):
        """
        Gets the number of edges that match a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        query_params = dict(action="count", q=json.dumps(query.to_dict()))
        return self._request("GET", "/edge", query_params=query_params)

    def delete_edges(self, query):
        """
        Deletes edges by a given query.

        `query` specifies the `EdgeQuery` to use.
        """
        query_params = dict(q=json.dumps(query.to_dict()))
        return self._request("DELETE", "/edge", query_params=query_params)

    def transaction(self, transaction):
        """
        Executes several requests in one HTTP request, as part of a
        single transaction.

        `transaction` specifies the `Transaction` to execute.
        """
        response = self._request("POST", "/transaction", body=transaction.payload)

        if self.raise_on_error:
            # Raise the first errored request
            for sub_response in response:
                if isinstance(sub_response, dict) and sub_response.get("error") != None:
                    raise Error(sub_response.get("code"), sub_response.get("error"))

        # Handle special serialization cases
        serialized_response = []
        for (req, res) in zip(transaction.payload, response):
            if req["action"] == "get_vertices":
                serialized_response.append([Vertex.from_dict(item) for item in res])
            elif req["action"] == "get_edges":
                serialized_response.append([Edge.from_dict(item) for item in res])
            else:
                serialized_response.append(res)

        return serialized_response

    def run_script(self, name, payload):
        """
        Executes a lua script.

        `name` specifies the name of the lua script, which should be in the server's script root directory. It should
        include the `.lua` extension of the file. `payload` is a JSON-serializable payload to send to the script.
        """
        return self._request("POST", _path("script", name), body=payload)
