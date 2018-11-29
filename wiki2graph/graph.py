class Concept:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.properties = {}

    def __str__(self):
        return "{}, from {}, with properties: {}".format(self.name, self.url, self.properties)


class Relation:
    def __init__(self, type, domain, range):
        self.type = type
        self.domain = domain
        self.range = range

    def __str__(self):
        return "{}({},{})".format(self.type, self.domain, self.range)


class Graph:
    def __init__(self, concepts=[], relations=[]):
        self.concepts = concepts
        self.relations = relations

    def extend(self, graph):
        self.concepts.extend(graph.concepts)
        self.relations.extend(graph.relations


def resolve_graph(graph):
    url_to_concept = {}
    for concept in graph.concepts:
        url_to_concept[concept.url] = concept
    for relation in graph.relations:
        if isinstance(relation.range, str):
            relation.range = url_to_concept[relation.range]


def get_cypher_for_graph(graph):
    """
    gets a cql string for the graph
    :param graph: a Graph
    :return: cql string
    """

    resolve_graph(graph)


class Extractor:
    # returns a list of concepts and/or relations
    def extract(self, soup):
        pass


def extract(crawler, extractors=[]):
    results = []
    for e in extractors:
        relations = e.extract(crawler)
        results.extend(relations)
    return results
