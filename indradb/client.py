import requests
import json
import itertools
from indradb.models import Vertex, Edge, VertexMetadata, EdgeMetadata, MapReducePing
from indradb.errors import Error

# Default time in seconds before a request times out
DEFAULT_REQUEST_TIMEOUT = 60

# Convenience function for building a path
_path = lambda *parts: "/%s" % "/".join(parts)

def stream_response(response):
    for line in response.iter_lines(decode_unicode=True):
        yield json.loads(line)

class Client(object):
    """Represents a connection to IndraDB"""

    def __init__(self, host, request_timeout=DEFAULT_REQUEST_TIMEOUT, scheme="https"):
        """
        Creates a new client.

        `host` specifies the hostname and port of the server, specified either as a tuple or a string of the format
        `hostname:port`.

        The optional `request_timeout` sets how many seconds to wait before a request times out (defaults to 60
        seconds.) The optional `scheme` sets what protocol to use (`http` or `https`.) This defaults to `https`,
        but if your server does not accept https requests, you will get an error.
        """

        if isinstance(host, tuple):
            self.host = host
        else:
            parts = host.split(":")
            self.host = (parts[0], int(parts[1]))

        self.scheme = scheme
        self.request_timeout = request_timeout
        self._session = requests.Session()

    def _request(self, method, endpoint, query_params=None, body=None, stream=False):
        """Makes a request"""

        response = self._session.request(method, "%s://%s:%s%s" % (self.scheme, self.host[0], self.host[1], endpoint),
            params=query_params,
            data=json.dumps(body) if body else None,
            timeout=self.request_timeout,
            stream=stream,
            headers={
                "content-type": "application/json"
            }
        )

        if response.status_code < 200 or response.status_code > 299:
            try:
                body = response.json()
            except Exception as e:
                body = None

            if isinstance(body, dict) and body.get("error") != None:
                raise Error(body.get("error"), code=response.status_code)
            else:
                raise Error("Unexpected response code", code=response.status_code)

        if stream:
            return stream_response(response)
        else:
            return response.json()

    def transaction(self, transaction):
        """
        Executes several requests in one HTTP request, as part of a
        single transaction.

        `transaction` specifies the `Transaction` to execute.
        """
        response = self._request("POST", "/transaction", body=transaction.payload)

        # Handle special serialization cases
        serialized_response = []

        for (req, res) in zip(transaction.payload, response):
            if isinstance(res, dict) and "error" in res:
                serialized_response.append(Error(res["error"]))
            else:
                action = req["action"]

                if action == "get_vertices":
                    serialized_response.append([Vertex.from_dict(item) for item in res])
                elif action == "get_edges":
                    serialized_response.append([Edge.from_dict(item) for item in res])
                elif action == "get_vertex_metadata":
                    serialized_response.append([VertexMetadata.from_dict(item) for item in res])
                elif action == "get_edge_metadata":
                    serialized_response.append([EdgeMetadata.from_dict(item) for item in res])
                else:
                    serialized_response.append(res)

        return serialized_response

    def script(self, name, payload):
        """
        Executes a lua script.

        `name` specifies the name of the lua script, which should be in the server's script root directory. It should
        include the `.lua` extension of the file. `payload` is a JSON-serializable payload to send to the script.
        """
        return self._request("POST", _path("script", name), body=payload)

    def mapreduce(self, name, payload):
        """
        Executes a lua mapreduce script.

        `name` specifies the name of the lua script, which should be in the server's script root directory. It should
        include the `.lua` extension of the file. `payload` is a JSON-serializable payload to send to the script.
        """

        for update in self._request("POST", _path("mapreduce", name), body=payload, stream=True):
            if "ping" in update:
                yield MapReducePing.from_dict(update["ping"])
            elif "ok" in update:
                yield update["ok"]
                return
            elif "error" in update:
                raise Error(update["error"])
            else:
                raise Error("Unexpected update: %s" % update)
