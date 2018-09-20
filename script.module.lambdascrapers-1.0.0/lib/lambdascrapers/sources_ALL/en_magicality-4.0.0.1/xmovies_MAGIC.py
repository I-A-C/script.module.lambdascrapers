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


import re,urlparse,json, traceback, urllib, time

from bs4 import BeautifulSoup

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser
from resources.lib.modules import debrid


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['xmovies8.tv', 'xmovies8.ru', 'xmovies8.es']
        self.base_link = 'https://xmovies8.nz'
        self.search_link = '/movies/search?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
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

    def searchShow(self, title, season, year, aliases, headers):
        try:

            clean_title = cleantitle.geturl(title).replace('-','+')
            url = urlparse.urljoin(self.base_link, self.search_link % ('%s+Season+%01d' % (clean_title, int(season))))
            r = self.scraper.get(url).content

            r = BeautifulSoup(r, 'html.parser').find('div', {'class': 'list_movies'})
            r = r.findAll(lambda tag: tag.name == 'a' and 'href' in tag.attrs)
            r = [i['href'] for i in r if '%s - Season %s' % (title, season) in i.text]

            return r[0]
        except:
            traceback.print_exc()
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            clean_title = cleantitle.geturl(title).replace('-','+')

            url = urlparse.urljoin(self.base_link, self.search_link % ('%s' %clean_title))
            r = self.scraper.get(url).content

            r = client.parseDOM(r, 'div', attrs={'class': 'list_movies'})
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [(i.attrs['href']) for i in r if i.content == '%s (%s)' %(title,year)]

            return r[0]
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            data = url

            aliases = data['aliases']
            headers = {}

            if 'tvshowtitle' in data:
                episode = int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], data['year'], aliases, headers)
            else:
                episode = 0
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            if url == None: return sources

            url = re.sub('/watching.html$', '', url.strip('/'))
            url = url + '/watching.html'

            p = self.scraper.get(url).text

            if episode > 0:
                p = BeautifulSoup(p, 'html.parser')
                p = p.find('div', {'class': 'ep_link'}).findAll('a')
                for i in p:
                    if 'Episode %s' % episode in i.text:
                        url = i['href']

                p = self.scraper.get(url).text

            referer = url

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                'Referer': url,
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://xmovies8.nu'
            }

            id = re.findall(r'load_player\(.+?(\d+)', p)[0]
            r = urlparse.urljoin(self.base_link, '/ajax/movie/load_player_v3?id=%s' % id)
            r = self.scraper.get(r, headers=headers).content

            url = json.loads(r)['value']

            if (url.startswith('//')):
                url = 'https:' + url

            url = url + '&_=%s' % int(time.time())

            r = self.scraper.get(url, headers=headers)
            headers = '|' + urllib.urlencode(headers)

            source = str(json.loads(r.text)['playlist'][0]['file']) + headers

            sources.append({'source': 'CDN', 'quality': 'HD', 'language': 'en', 'url': source, 'direct': True, 'debridonly': False})

            return sources
        except:
            traceback.print_exc()
            return sources


    def resolve(self, url):
        return url
