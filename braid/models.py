DEFAULT_LIMIT = 1000

class Vertex(object):
    def __init__(self, id, type):
        self.id = id
        self.type = type

    @classmethod
    def from_dict(cls, d):
        return cls(id=d["id"], type=d["type"])

class EdgeKey(object):
    def __init__(self, outbound_id, type, inbound_id):
        self.outbound_id = outbound_id
        self.type = type
        self.inbound_id = inbound_id

    @classmethod
    def from_dict(cls, d):
        return cls(
            outbound_id=d["outbound_id"],
            type=d["type"],
            inbound_id=d["inbound_id"]
        )

class Edge(object):
    def __init__(self, key, weight, update_datetime):
        self.key = key
        self.weight = weight
        self.update_datetime = update_datetime

    @classmethod
    def from_dict(cls, d):
        return cls(
            key=EdgeKey.from_dict(d["key"]),
            weight=d["weight"],
            update_datetime=d["update_datetime"],
        )

class VertexQuery(object):
    def __init__(self, query):
        self._query = query

    @classmethod
    def all(cls, id, limit):
        return cls(dict(all=(id, limit)))

    @classmethod
    def vertex(cls, id):
        return cls(dict(vertex=id))

    @classmethod
    def vertices(cls, ids):
        return cls(dict(vertices=ids))

    @classmethod
    def _pipe(cls, query, query_type_converter, limit=DEFAULT_LIMIT):
        return cls(dict(pipe=(query, query_type_converter, limit)))

    def outbound_edges(self, type=None, high=None, low=None, limit=DEFAULT_LIMIT):
        return EdgeQuery._pipe(self._query, "outbound", type=type, high=high, low=low, limit=limit)

    def inbound_edges(self, type=None, high=None, low=None, limit=DEFAULT_LIMIT):
        return EdgeQuery._pipe(self._query, "inbound", type=type, high=high, low=low, limit=limit)

class EdgeQuery(object):
    def __init__(self, query):
        self._query = query

    @classmethod
    def edge(cls, outbound_id, type, inbound_id):
        return cls(dict(edge=(outbound_id, type, inbound_id)))

    @classmethod
    def edges(cls, edges):
        return cls(dict(edges=edges))

    @classmethod
    def _pipe(cls, query, query_type_converter, type=None, high=None, low=None, limit=DEFAULT_LIMIT):
        return cls(dict(pipe=(query, query_type_converter, type, high, low, limit)))

    def outbound_vertices(self, limit=DEFAULT_LIMIT):
        return VertexQuery._pipe(self._query, "outbound", limit=limit)

    def inbound_vertices(self, limit=DEFAULT_LIMIT):
        return VertexQuery._pipe(self._query, "inbound", limit=limit)
