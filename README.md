# wiki2graph

A wiki crawler to populate a neo4j graph database.

## Development installation

1. Download [Neo4j](https://neo4j.com/download/)
2. After your download, they will take you to a guide for your OS, follow that (making your password "password").  Go until "Explore Sample Datasets".([Sample walkthrough link for OS X](https://neo4j.com/download-thanks-desktop/?edition=desktop&flavour=osx&release=1.1.17&offline=true))
3. At this point, you should have a graph going.
4. It's recommended you have a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/)
5. `pip install -r requirements.txt`
6. The pokemon graph extractor:  `python wiki2graph/pokemon/go.py`

## Production deployment

For now, as Development installation

## Example usage

The [pokemon extractor](wiki2graph/pokemon/go.py) is a "plug in" for the crawler that lets it recognize pokemon-related entities and relations.

Creating an extractor for another domain requires two parts:

1. Create an extractor that inherits from Extractor (in wiki2graph.graph) 

```class PokemonExtractor(Extractor)```

2. When you create your crawler, send a list of the extractors you created (NOTE: currently doesn't work this way but it should) 

```c = Crawler('http://pokemon.wikia.com', '/wiki/Bulbasaur', limit=800, extractors=[YOUR EXTRACTORS HERE])```