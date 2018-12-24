import json
import re

from neo4j.v1 import GraphDatabase


class Concept:
    def __init__(self, type, url, properties={}):
        self.type = type
        self.url = url
        self.properties = properties
        self.properties['url'] = self.url

    def __str__(self):
        return "{}, from {}, with properties: {}".format(self.type, self.url, self.properties)

    def __eq__(self, other):
        return other.url == self.url

    def __hash__(self):
        return self.url.__hash__()


class Relation:
    def __init__(self, type, domain, range):
        self.type = type
        self.domain = domain
        self.range = range

    def __str__(self):
        return "{}({},{})".format(self.type, self.domain, self.range)


class Graph:
    def __init__(self, concepts=set(), relations=set()):
        self.concepts = concepts
        self.relations = relations

    def extend(self, rhs):
        self.concepts.union(rhs.concepts)
        self.relations.union(rhs.relations)


def resolve_graph(graph):
    url_to_concept = {}
    for concept in graph.concepts:
        url_to_concept[concept.url] = concept
    for relation in graph.relations:
        if isinstance(relation.range, str) and relation.range in url_to_concept:
            relation.range = url_to_concept[relation.range]


def get_cypher_for_graph(graph, sep='WITH count(*) AS f'):
    """
    gets a cql string for the graph
    :param graph: a Graph
    :return: list of cypher statements
    """

    resolve_graph(graph)

    cql = []
    for concept in graph.concepts:
        query = 'MERGE (a:{} {}){}'.format(concept.type, json.dumps(concept.properties), sep)
        query = re.sub(r'(?<!: )"(\S*?)"', '\\1', query)
        cql.append(query)
    # cql = re.sub(r'(?<!: )"(\S*?)"', '\\1', cql)
    # cql += '\n\n'
    for relation in graph.relations:
        if not isinstance(relation.range, str):
            cql.append('MATCH (domain:{}) where domain.url = \"{}\"\n' \
                       'OPTIONAL MATCH (range:{}) where range.url = \"{}\"\n' \
                       'MERGE (domain)-[:{}]->(range) {}\n'.format(
                relation.domain.type,
                relation.domain.url,
                relation.range.type,
                relation.range.url,
                relation.type,
                sep
            ))
    # cql = cql[:len(cql) - len(sep) - 2]  # remove last WITH AS
    return cql


def save_graph_to_neo(graph, uri, user, password):
    graph_db = GraphDatabase.driver(uri, auth=(user, password))

    with graph_db.session() as session:
        for query in get_cypher_for_graph(graph, ';'):
            session.write_transaction(lambda tx: tx.run(query))

    graph_db.close()


class Extractor:

    # returns a list of concepts and/or relations
    def extract(self, soup):
        """
        extract graph from page
        :param soup: the bs4 object from the crawler
        :return: a graph
        """
        pass


def extract(crawler, extractors=[]):
    results = Graph()
    for e in extractors:
        results.extend(e.extract(crawler))
    return results
