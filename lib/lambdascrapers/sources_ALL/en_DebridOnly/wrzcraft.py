# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo


import re,urlparse, urllib, requests,traceback

from bs4 import BeautifulSoup

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid
from resources.lib.modules import source_utils
from resources.lib.modules import cfscrape

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['wrzcraft.net']
        self.base_link = 'http://wrzcraft.net'
        self.search_link = '/search/%s/feed/rss2/'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            scraper = cfscrape.create_scraper()
            url = {'imdb': imdb, 'title': title, 'year': year}
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:

            if url == None: return sources

            if debrid.status() == False: raise Exception()

            data = url

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = requests.get(url).text
            posts = re.findall(r'(?s)<item>(.*?)</item>', r)

            hostDict = hostprDict + hostDict

            items = []
            for post in posts:
                try:
                    title = re.findall(r'<title>(.*?)</title>', post)[0]
                    if query.lower() in title.lower():
                        linksDivs = re.findall(r'(?s)<singlelink></singlelink><br />(.*?)<br />.<strong>', post)
                        for div in linksDivs:
                            links = re.findall(r'<a href="(.*?)"', div)
                            for link in links:
                                quality = source_utils.get_quality_simple(link)
                                valid, host = source_utils.is_host_valid(link, hostDict)
                                if valid:
                                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': '', 'direct': False, 'debridonly': True})

                except:
                    traceback.print_exc()
                    pass
            return sources
        except:
            traceback.print_exc()
            return sources


    def resolve(self, url):
        return url

