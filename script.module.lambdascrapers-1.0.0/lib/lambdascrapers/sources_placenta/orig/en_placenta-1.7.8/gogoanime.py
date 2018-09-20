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


import re,traceback,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import source_utils
from resources.lib.modules import tvmaze


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['gogoanimemobile.com', 'gogoanimemobile.net', 'gogoanime.io']
        self.base_link = 'https://www2.gogoanime.se/'
        self.search_link = '/search.html?keyword=%s'
        self.episode_link = '/%s-episode-%s'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            tv_maze = tvmaze.tvMaze()
            tvshowtitle = tv_maze.showLookup('thetvdb', tvdb)
            tvshowtitle = tvshowtitle['name']

            t = cleantitle.get(tvshowtitle)

            q = urlparse.urljoin(self.base_link, self.search_link)
            q = q % urllib.quote_plus(tvshowtitle)

            r = client.request(q)

            r = client.parseDOM(r, 'ul', attrs={'class': 'items'})
            r = client.parseDOM(r, 'li')
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title'), re.findall('\d{4}', i)) for i in r]
            r = [(i[0][0], i[1][0], i[2][-1]) for i in r if i[0] and i[1] and i[2]]
            r = [i for i in r if t == cleantitle.get(i[1]) and year == i[2]]
            r = r[0][0]

            url = re.findall('(?://.+?|)(/.+)', r)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('GoGoAnime - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            tv_maze = tvmaze.tvMaze()
            num = tv_maze.episodeAbsoluteNumber(tvdb, int(season), int(episode))

            url = [i for i in url.strip('/').split('/')][-1]
            url = self.episode_link % (url, num)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('GoGoAnime - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            r = client.parseDOM(r, 'iframe', ret='src')

            for u in r:
                try:
                    if not u.startswith('http') and not 'vidstreaming' in u: raise Exception()

                    url = client.request(u)
                    url = client.parseDOM(url, 'source', ret='src')

                    for i in url:
                        try: sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                        except: pass
                except:
                    pass

            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('GoGoAnime - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return directstream.googlepass(url)


