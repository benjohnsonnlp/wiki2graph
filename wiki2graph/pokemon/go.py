from wiki2graph.crawler import Crawler
from wiki2graph.graph import extract, Extractor


class PokemonExtractor(Extractor):
    def extract(self, soup):
        return []


if __name__ == '__main__':
    c = Crawler('http://pokemon.wikia.com/wiki/Pokémon_Wiki', limit=200)

    for thing in c:
        print(extract(thing, extractors=[
            PokemonExtractor(),
        ]))
