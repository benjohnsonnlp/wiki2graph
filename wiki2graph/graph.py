class Concept:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.properties = {}


class Relation:
    def __init__(self, domain, range):
        self.domain = domain
        self.range = range


class Extractor:
    # returns a list of concepts and/or relations
    def extract(self, soup):
        pass


def extract(crawler, extractors=[]):
    results = []
    for e in extractors:
        relations = e.extract(soup=crawler.soup)
        results.extend(relations)
    return results
