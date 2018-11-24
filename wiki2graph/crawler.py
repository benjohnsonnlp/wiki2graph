import json
import logging
import os
from heapq import heappop, heappush

import requests
from bs4 import BeautifulSoup

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)


class DefaultPrioritizationScheme:
    def __init__(self, crawler):
        self.crawler = crawler

    def prioritize_pages(self, pages):
        output = []
        for page in pages:
            output.append(self.prioritize(page))
        return output

    def prioritize(self, page):
        output = None
        if page.startswith('/wiki'):
            output = (50, page)  # assign a mid level priority to pages in the wiki
        else:
            pass  # don't put in pages that aren't in the base url
        return output


class Crawler:
    def __init__(self, base_url, cache="cache/", prioritization_scheme=DefaultPrioritizationScheme, limit=100):
        self.base_url = base_url
        self.limit = limit

        # create the cache_dir if not there
        self.cache_dir = cache
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # load the cache dictionary
        try:
            with open(os.path.join(self.cache_dir, 'cache_dict.json')) as f:
                self.cache_dict = json.load(f)
        except FileNotFoundError:
            logger.warning("No cache found, creating...")
            with open(os.path.join(self.cache_dir, 'cache_dict.json'), 'w') as f:
                self.cache_dict = {}
                json.dump(self.cache_dict, f, indent=4)

        self.visited = []

        self.next_pages = [(1, base_url)]
        self.prioritization_scheme = prioritization_scheme(self)

        self.current_page = None
        self.html = ''
        self.soup = None

        next(self)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.next_pages or len(self.visited) == self.limit:
            return None

        self.current_page = heappop(self.next_pages)[1]
        while self.current_page in self.visited:
            self.current_page = heappop(self.next_pages)[1]

        # get the next page, either from the cache or the web
        if self.current_page in self.cache_dict:
            logger.info("Cache hit on {}".format(self.current_page))
            with open(os.path.join(self.cache_dir, self.cache_dict[self.current_page]), encoding='utf-8') as f:
                self.html = '\n'.join(f.readlines())
        else:
            logger.info('Getting page: {}'.format(self.current_page))
            page_to_get = self.current_page  # for handling relative URLs
            if self.current_page.startswith('/'):
                page_to_get = self.base_url + self.current_page
            self.html = requests.get(page_to_get).text
            self.cache_current()

        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.visited.append(self.current_page)
        self.get_next_pages()
        return self

    def get_next_pages(self):
        for link in self.soup.find_all('a'):
            if 'href' in link.attrs:
                link = link.attrs['href']
                if link in self.visited:
                    continue  # already been there, don't need to go again
                prioritized = self.prioritization_scheme.prioritize(link)
                if prioritized:
                    heappush(self.next_pages, prioritized)

    def cache_current(self):
        file_id = 'page-{}.html'.format((len(self.cache_dict) + 1))
        self.cache_dict[self.current_page] = file_id
        # save cache_dict
        with open(os.path.join(self.cache_dir, 'cache_dict.json'), 'w') as f:
            json.dump(self.cache_dict, f, indent=4)

        # save html
        with open(os.path.join(self.cache_dir, file_id), 'w', encoding='utf-8') as f:
            f.write(self.html)

    def current_title(self):
        return self.soup.find_all('title')[0].text


if __name__ == '__main__':
    c = Crawler('http://pokemon.wikia.com/wiki/Pokémon_Wiki', limit=200)

    for thing in c:
        print(thing.current_title())
