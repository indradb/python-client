class Transaction(object):
    def __init__(self):
        self.payload = []

    def _add(self, **kwargs):
        self.payload.append(kwargs)

    def create_vertex(self, type):
        self._add(action="create_vertex", type=type)

    def get_vertices(self, query):
        self._add(action="get_vertices", query=query._query)

    def set_vertices(self, query, weight):
        self._add(action="set_vertices", query=query._query, weight=weight)

    def delete_vertices(self, query):
        self._add(action="delete_vertices", query=query._query)

    def create_edge(self, key, weight):
        key_dict = dict(outbound_id=key.outbound_id, type=key.type, inbound_id=key.inbound_id)
        self._add(action="create_edge", key=key_dict, weight=weight)

    def get_edges(self, query):
        self._add(action="get_edges", query=query._query)

    def set_edges(self, query, weight):
        self._add(action="set_edges", query=query._query, weight=weight)

    def delete_edges(self, query):
        self._add(action="delete_edges", query=query._query)

    def get_edge_count(self, query):
        self._add(action="get_edge_count", query=query._query)

    def run_script(self, name, payload):
        self._add(action="run_script", name=name, payload=payload)
