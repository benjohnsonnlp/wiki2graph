import logging

from wiki2graph.crawler import Crawler
from wiki2graph.graph import extract, Extractor, Concept


class PokemonExtractor(Extractor):
    def extract(self, crawler):
        soup = crawler.soup
        is_pokemon_page = soup.find('.PokéBox')
        if not is_pokemon_page:
            return []

        print("pokemon found for {}".format(crawler.current_title()))
        # ok we have a pokemon
        name = soup.file_all('.page-header__title').text
        pokemon_object = Concept(name, crawler.current_page)

        # image
        image = soup.find_all('.PokéBox img')[1].attrs['src']
        pokemon_object.properties['image'] = image

        # evolution relation

        return [
            pokemon_object
        ]



if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    c = Crawler('http://pokemon.wikia.com', 'http://pokemon.wikia.com/wiki/Pokémon_Wiki', limit=200)

    for thing in c:
        # print("extracting for {}".format(thing.current_title()))
        print(extract(thing, extractors=[
            PokemonExtractor(),
        ]))
