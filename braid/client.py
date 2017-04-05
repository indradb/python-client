import requests
import json
import itertools
from .models import Vertex, Edge
from .errors import BraidError

DEFAULT_REQUEST_TIMEOUT = 60

_path = lambda *parts: "/%s" % "/".join(parts)
_format_date = lambda d: d.isoformat("T") + "Z" if d else None

class Client(object):
    def __init__(self, host, email, secret, request_timeout=DEFAULT_REQUEST_TIMEOUT, raise_on_error=True, scheme="https"):
        if isinstance(host, tuple):
            self.host = host
        else:
            parts = host.split(":")
            self.host = (parts[0], int(parts[1]))

        self.scheme = scheme
        self.email = email
        self.secret = secret
        self.request_timeout = request_timeout
        self.raise_on_error = raise_on_error
        self._session = requests.Session()

    def _request(self, method, endpoint, query_params=None, body=None):
        response = self._session.request(method, "%s://%s:%s%s" % (self.scheme, self.host[0], self.host[1], endpoint),
            params=query_params,
            data=json.dumps(body) if body else None,
            timeout=self.request_timeout,
            auth=(self.email, self.secret),
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
                raise BraidError(response.status_code, body.get("error"))
            else:
                raise BraidError(response.status_code, "Unexpected response code")

        return response.json()

    def create_vertex(self, type):
        query_params = dict(type=type)
        return self._request("POST", "/vertex", query_params)

    def get_vertices(self, query):
        query_params = dict(q=json.dumps(query._query))
        response = self._request("GET", "/vertex", query_params=query_params)
        return [Vertex.from_dict(item) for item in response]

    def set_vertices(self, query, weight):
        query_params = dict(q=json.dumps(query._query), weight=weight)
        return self._request("PUT", "/vertex", query_params=query_params)

    def delete_vertices(self, query):
        query_params = dict(q=json.dumps(query._query))
        return self._request("DELETE", "/vertex", query_params=query_params)

    def create_edge(self, key, weight):
        query_params = dict(weight=weight)
        return self._request("PUT", _path("edge", key.outbound_id, key.type, key.inbound_id), query_params=query_params)

    def get_edges(self, query):
        query_params = dict(q=json.dumps(query._query))
        response = self._request("GET", "/edge", query_params=query_params)
        return [Edge.from_dict(item) for item in response]

    def get_edge_count(self, query):
        query_params = dict(action="count", q=json.dumps(query._query))
        return self._request("GET", "/edge", query_params=query_params)

    def delete_edges(self, query):
        query_params = dict(q=json.dumps(query._query))
        return self._request("DELETE", "/edge", query_params=query_params)

    def transaction(self, transaction):
        response = self._request("POST", "/transaction", body=transaction.payload)

        if self.raise_on_error:
            for sub_response in response:
                if isinstance(sub_response, dict) and sub_response.get("error") != None:
                    raise BraidError(sub_response.get("code"), sub_response.get("error"))

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
        return self._request("POST", _path("script", name), body=payload)
