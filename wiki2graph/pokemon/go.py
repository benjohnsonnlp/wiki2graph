import logging

from wiki2graph.crawler import Crawler
from wiki2graph.graph import extract, Extractor, Concept, Relation, Graph, get_cypher_for_graph

logger = logging.getLogger(__name__)


def get_tr_with_label(soup, label):
    evolves_into_label = soup.find(lambda x: x.text.strip().startswith(label))
    return evolves_into_label


class PokemonExtractor(Extractor):
    def extract(self, crawler):
        soup = crawler.soup
        graph = Graph()
        is_pokemon_page = soup.find('table', class_="PokeBox")
        if not is_pokemon_page:
            return graph

        high_priority_urls = []

        logger.info("Parsing pokemon found for {}".format(crawler.current_title()))
        # ok we have a pokemon
        name = soup.select('.page-header__title')[0].text
        pokemon_object = Concept("Pokemon", crawler.current_page, {'name': name})

        # image
        image = soup.select('.PokeBox img')[0].attrs['src']
        pokemon_object.properties['image'] = image
        logger.info("Adding {} to the graph...".format(pokemon_object))
        graph.concepts.add(pokemon_object)

        # evolution relation
        evolves_into_label = get_tr_with_label(soup, "Evolves into")
        links = evolves_into_label.find('a')
        if links:
            evolves_into_url = links.attrs['href'].strip()
            evolves_into = Relation('evolves_into', pokemon_object, evolves_into_url)
            high_priority_urls.append(evolves_into_url)
            graph.relations.add(evolves_into)

        abilites_label = get_tr_with_label(soup, "Abilities")

        for item in abilites_label.contents[2].select('a'):
            url = item.attrs['href'].strip()
            graph.relations.add(Relation('has_ability', pokemon_object, url))
            high_priority_urls.append(url)

        for url in high_priority_urls:
            logger.info("Adding {} to crawler list with highest priority...".format(url))
            crawler.add_url_with_priority(url, 1)

        return graph


class SkillExtractor(Extractor):
    def extract(self, crawler):
        soup = crawler.soup

        graph = Graph()
        move_name = soup.select('#movename')
        if move_name:
            name = move_name[0].text
            ability = Concept('Ability', crawler.current_page, {'name': name})
            logger.info('Adding {} to the graph...'.format(name))
            graph.concepts.add(ability)
            return graph

        cats = soup.select('ul.categories a')
        use_header = False
        for cat in cats:
            if cat.text == 'Abilities':
                use_header = True
                break
        if use_header:
            name = soup.select('.page-header__title')[0].text
            ability = Concept('Ability', crawler.current_page, {'name': name})
            logger.info('Adding {} to the graph...'.format(name))
            graph.concepts.add(ability)

        return graph


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    # c = Crawler('http://pokemon.wikia.com', 'http://pokemon.wikia.com/wiki/Pokémon_Wiki', limit=200)
    g = Graph()
    # c = Crawler('http://pokemon.wikia.com', '/wiki/Category:Generation_I_Pok%C3%A9mon', limit=400)
    c = Crawler('http://pokemon.wikia.com', '/wiki/Bulbasaur', limit=400)
    # g.extend(extract(c, extractors=[PokemonExtractor(), ]))
    for thing in c:
        g.extend(extract(c, extractors=[PokemonExtractor(), SkillExtractor(), ]))
        logger.info('Graph now has {} concepts and {} relations.'.format(len(g.concepts), len(g.relations)))

    with open('poke.cql', 'w') as f:
        f.write(get_cypher_for_graph(g))
