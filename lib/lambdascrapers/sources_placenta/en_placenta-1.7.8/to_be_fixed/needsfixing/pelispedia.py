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


import re,urllib,urlparse,json,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import jsunpack
from resources.lib.modules import trakt
from resources.lib.modules import tvmaze
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['pelispedia.tv']
        self.base_link = 'http://www.pelispedia.tv'
        self.moviesearch_link = '/pelicula/%s/'
        self.tvsearch_link = '/serie/%s/'
        self.protect_link = 'http://player.pelispedia.tv/template/protected.php'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(self.moviesearch_link, title, year)
            if not url: url = self.__search(self.tvsearch_link, title + '-', year)
            if not url: url = self.__search(self.moviesearch_link, trakt.getMovieTranslation(imdb, 'es'), year)
            return url
        except:
            pass

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search(self.tvsearch_link, tvshowtitle, year)
            if not url: url = self.__search(self.tvsearch_link, tvshowtitle + '-', year)
            if not url: url = self.__search(self.tvsearch_link, tvmaze.tvMaze().getTVShowTranslation(tvdb, 'es'), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            r = client.request(urlparse.urljoin(self.base_link, url))
            r = dom_parser.parse_dom(r, 'article', {'class': 'SeasonList'})
            r = dom_parser.parse_dom(r, 'ul')
            r = dom_parser.parse_dom(r, 'li')
            r = dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('[^"]+-season-%s-episode-%s(?!\d)[^"]*' % (season, episode))}, req='href')[0].attrs['href']

            return source_utils.strip_domain(r)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)
            r = dom_parser.parse_dom(r, 'div', {'class': 'repro'})

            r = dom_parser.parse_dom(r[0].content, 'iframe', req='src')
            f = r[0].attrs['src']

            r = client.request(f)
            r = dom_parser.parse_dom(r, 'div', {'id': 'botones'})
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [(i.attrs['href'], urlparse.urlparse(i.attrs['href']).netloc) for i in r]

            links = []

            for u, h in r:
                if not 'pelispedia' in h:
                    valid, host = source_utils.is_host_valid(u, hostDict)
                    if not valid: continue

                    links.append({'source': host, 'quality': 'SD', 'url': u, 'direct': False})
                    continue

                result = client.request(u, headers={'Referer': f}, timeout='10')

                try:
                    if 'pelispedia' in h: raise Exception()

                    url = re.findall('sources\s*:\s*\[(.+?)\]', result)[0]
                    url = re.findall('file\s*:\s*(?:\"|\')(.+?)(?:\"|\')\s*,\s*label\s*:\s*(?:\"|\')(.+?)(?:\"|\')', url)
                    url = [i[0] for i in url if '720' in i[1]][0]

                    links.append({'source': 'cdn', 'quality': 'HD', 'url': url, 'direct': False})
                except:
                    pass

                try:
                    url = re.findall('sources\s*:\s*\[(.+?)\]', result)[0]
                    url = re.findall('file\s*:\s*(?:\"|\')(.+?)(?:\"|\')', url)

                    for i in url:
                        try:
                            links.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'url': i, 'direct': True})
                        except:
                            pass
                except:
                    pass

                try:
                    post = re.findall('gkpluginsphp.*?link\s*:\s*"([^"]+)', result)[0]
                    post = urllib.urlencode({'link': post})

                    url = urlparse.urljoin(self.base_link, '/gkphp_flv/plugins/gkpluginsphp.php')
                    url = client.request(url, post=post, XHR=True, referer=u, timeout='10')
                    url = json.loads(url)['link']

                    links.append({'source': 'gvideo', 'quality': 'HD', 'url': url, 'direct': True})
                except:
                    pass

                try:
                    post = re.findall('var\s+parametros\s*=\s*"([^"]+)', result)[0]

                    post = urlparse.parse_qs(urlparse.urlparse(post).query)['pic'][0]
                    post = urllib.urlencode({'sou': 'pic', 'fv': '25', 'url': post})

                    url = client.request(self.protect_link, post=post, XHR=True, timeout='10')
                    url = json.loads(url)[0]['url']

                    links.append({'source': 'cdn', 'quality': 'HD', 'url': url, 'direct': True})
                except:
                    pass

                try:
                    if not jsunpack.detect(result): raise Exception()

                    result = jsunpack.unpack(result)
                    url = re.findall('sources\s*:\s*\[(.+?)\]', result)[0]
                    url = re.findall('file\s*:\s*.*?\'(.+?)\'', url)
                    for i in url:
                        try:
                            i = client.request(i, headers={'Referer': f}, output='geturl', timeout='10')
                            links.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'url': i,
                                          'direct': True})
                        except:
                            pass
                except:
                    pass

                try:
                    post = re.findall('var\s+parametros\s*=\s*"([^"]+)', result)[0]

                    post = urlparse.parse_qs(urlparse.urlparse(post).query)['pic'][0]
                    token = 'eyJjdCI6InZGS3QySm9KRWRwU0k4SzZoZHZKL2c9PSIsIml2IjoiNDRkNmMwMWE0ZjVkODk4YThlYmE2MzU0NDliYzQ5YWEiLCJzIjoiNWU4MGUwN2UwMjMxNDYxOCJ9'
                    post = urllib.urlencode({'sou': 'pic', 'fv': '0', 'url': post, 'token': token})

                    url = client.request(self.protect_link, post=post, XHR=True, timeout='10')
                    js = json.loads(url)
                    url = [i['url'] for i in js]
                    for i in url:
                        try:
                            i = client.request(i, headers={'Referer': f}, output='geturl', timeout='10')
                            links.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'url': i, 'direct': True})
                        except:
                            pass
                except:
                    pass

            for i in links: sources.append({'source': i['source'], 'quality': i['quality'], 'language': 'en', 'url': i['url'], 'direct': i['direct'], 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, search_url, title, year):
        try:
            url = search_url % cleantitle.geturl(title)

            r = urlparse.urljoin(self.base_link, url)
            r = client.request(r, limit='1', timeout='10')
            r = dom_parser.parse_dom(r, 'title')[0].content
            return url if year in r else None
        except:
            pass


