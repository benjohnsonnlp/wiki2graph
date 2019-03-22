import logging
# so it can be called from parent dir and without PYTHONPATH=.:$PYTHONPATH
import os
import sys
from threading import Thread

sys.path.append(os.getcwd())

from wiki2graph.crawler import Crawler
from wiki2graph.graph import Extractor, Concept, Relation, Graph, save_graph_to_neo, get_cypher_for_graph, extract

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

        # get ability info
        abilites_label = get_tr_with_label(soup, "Abilities")

        for item in abilites_label.contents[2].select('a'):
            url = item.attrs['href'].strip()
            graph.relations.add(Relation('has_ability', pokemon_object, url))
            high_priority_urls.append(url)

        # Add pokemon typing
        types_label = get_tr_with_label(soup, "Type(s)")

        for item in types_label.find_all('a'):
            if "type" in item['title'].strip():
                type_url = item.attrs['href'].strip()
                graph.relations.add(Relation('has_type', pokemon_object, type_url))
                high_priority_urls.append(type_url)

        # pokedex relation
        # TODO:  BUG somehow this is getting reversed
        pokedex = get_tr_with_label(soup, "Pokedex")
        if pokedex:
            next_pokedex = [a.attrs['href'] for a in
                            list(get_tr_with_label(soup, "Pokedex").next_elements)[4].select('a')]
            high_priority_urls.extend(next_pokedex)
            for item in next_pokedex:
                graph.relations.add(Relation('next_in_pokedex', pokemon_object, item))

        # add URLs for other entities into crawler priority queue
        # TODO: work this into object scheme better
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

            skill_type = soup.find_all("span", class_="t-type")[0].find('a').attrs['href'].strip()
            graph.relations.add(Relation('is_type', ability, skill_type))
            
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
            skill_type = soup.find_all("span", class_="t-type")
            if len(skill_type) >= 1:
                skill_type = skill_type[0].find('a').attrs['href'].strip()
                graph.relations.add(Relation('is_type', ability, skill_type))

        return graph

class TypeExtractor(Extractor):
    def extract(self, crawler):
        soup = crawler.soup

        graph = Graph()
        cats = soup.select('ul.categories a')
        for cat in cats:
            if cat.text == 'Types':
                name = soup.select('.page-header__title')[0].text.strip().split()
                pokemon_type = Concept('Type', crawler.current_page, {'name': name[0]})
                logger.info('Adding {} to the graph...'.format(name[0]))
                graph.concepts.add(pokemon_type)

                titles = soup.find_all("span", class_='mw-headline')
                for title in titles:
                    if "Effectiveness" in title.text:
                        superEffect = title.find_next('pre')
                        for strong in superEffect.find_all('a'):
                            url = strong.attrs['href']
                            if name[0] in url:
                                url = crawler.current_page
                            graph.relations.add(Relation('super_effective_against', pokemon_type, url))

                        notVeryEffect = superEffect.find_next('pre')
                        for weak in notVeryEffect.find_all('a'):
                            url = weak.attrs['href']
                            if name[0] in url:
                                url = crawler.current_page
                            graph.relations.add(Relation('not_very_effective_against', pokemon_type, url))
                        
                        inEffect = notVeryEffect.find_next('pre')
                        if inEffect:
                            for nothing in inEffect.find_all('a'):
                                url = nothing.attrs['href']
                                if name[0] in url:
                                    url = crawler.current_page
                                graph.relations.add(Relation('ineffective_against', pokemon_type, url))

                

        return graph

if __name__ == '__main__':

    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    # c = Crawler('http://pokemon.wikia.com', 'http://pokemon.wikia.com/wiki/Pokémon_Wiki', limit=200)
    g = Graph()
    # c = Crawler('http://pokemon.wikia.com', '/wiki/Category:Generation_I_Pok%C3%A9mon', limit=400)
    c = Crawler('http://pokemon.wikia.com', '/wiki/Bulbasaur', limit=800)
    # g.extend(extract(c, extractors=[PokemonExtractor(), ]))
    for thing in c:
        g.extend(extract(c, extractors=[PokemonExtractor(), SkillExtractor(), TypeExtractor(), ]))


        # TODO: make graph creds configurable
        def save_graph():
            save_graph_to_neo(g, "bolt://localhost:7687", 'neo4j', 'password')


        t = Thread(target=save_graph)
        t.run()

        logger.info('Graph now has {} concepts and {} relations.'.format(len(g.concepts), len(g.relations)))

    with open('poke.cql', 'w') as f:
        f.write('\n'.join(get_cypher_for_graph(g)))
