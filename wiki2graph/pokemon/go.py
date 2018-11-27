import logging

from wiki2graph.crawler import Crawler
from wiki2graph.graph import extract, Extractor, Concept, Relation


class PokemonExtractor(Extractor):
    def extract(self, crawler):
        soup = crawler.soup
        is_pokemon_page = soup.find('table', class_="PokeBox")
        if not is_pokemon_page:
            return []

        print("pokemon found for {}".format(crawler.current_title()))
        # ok we have a pokemon
        name = soup.select('.page-header__title')[0].text
        pokemon_object = Concept(name, crawler.current_page)

        # image
        image = soup.select('.PokeBox img')[0].attrs['src']
        pokemon_object.properties['image'] = image

        # evolution relation
        evolves_into_label = soup.find(lambda x: x.text.strip().startswith("Evolves into"))
        evolves_into_url = evolves_into_label.contents[2].contents[0].attrs['href'].strip()
        evolves_into = Relation('evolves-into', pokemon_object, evolves_into_url)

        return [
            pokemon_object,
            evolves_into,
        ]


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    # c = Crawler('http://pokemon.wikia.com', 'http://pokemon.wikia.com/wiki/Pokémon_Wiki', limit=200)
    c = Crawler('http://pokemon.wikia.com', '/wiki/Abra', limit=200)

    # for thing in c:
    # print("extracting for {}".format(thing.current_title()))
    print(['' + item.__str__() for item in extract(c, extractors=[
        PokemonExtractor(),
    ])])
