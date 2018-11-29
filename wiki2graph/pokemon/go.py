import logging

from wiki2graph.crawler import Crawler
from wiki2graph.graph import extract, Extractor, Concept, Relation, Graph

logger = logging.getLogger(__name__)


def get_tr_with_label(soup, label):
    evolves_into_label = soup.find(lambda x: x.text.strip().startswith(label))
    return evolves_into_label


class PokemonExtractor(Extractor):
    def extract(self, crawler):
        soup = crawler.soup
        is_pokemon_page = soup.find('table', class_="PokeBox")
        if not is_pokemon_page:
            return []

        high_priority_urls = []

        logger.info("Parsing pokemon found for {}".format(crawler.current_title()))
        # ok we have a pokemon
        name = soup.select('.page-header__title')[0].text
        pokemon_object = Concept(name, crawler.current_page)

        # image
        image = soup.select('.PokeBox img')[0].attrs['src']
        pokemon_object.properties['image'] = image

        graph = Graph(concepts=[pokemon_object])

        # evolution relation
        evolves_into_label = get_tr_with_label(soup, "Evolves into")
        links = evolves_into_label.find('a')
        if links:
            evolves_into_url = links.attrs['href'].strip()
            evolves_into = Relation('evolves-into', pokemon_object, evolves_into_url)
            high_priority_urls.append(evolves_into_url)
            graph.relations.append(evolves_into)

        abilites_label = get_tr_with_label(soup, "Abilities")

        for item in abilites_label.contents[2].select('a'):
            url = item.attrs['href'].strip()
            graph.relations.append(Relation('has-ability', pokemon_object, url))
            high_priority_urls.append(url)

        for url in high_priority_urls:
            logger.info("Adding {} to crawler list with highest priority...".format(url))
            crawler.add_url_with_priority(url, 1)

        return graph


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    # c = Crawler('http://pokemon.wikia.com', 'http://pokemon.wikia.com/wiki/Pokémon_Wiki', limit=200)
    graph = Graph()
    c = Crawler('http://pokemon.wikia.com', '/wiki/Abra', limit=200)
    graph.extend(extract(c, extractors=[PokemonExtractor(), ]))
    for thing in c:
        graph.extend(extract(c, extractors=[PokemonExtractor(), ]))
