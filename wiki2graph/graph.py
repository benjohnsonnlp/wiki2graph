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
