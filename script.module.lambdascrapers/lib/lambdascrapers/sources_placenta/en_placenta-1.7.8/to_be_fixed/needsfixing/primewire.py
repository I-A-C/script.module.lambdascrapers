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


import re,urllib,urlparse,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import proxy
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['primewire.is']
        self.base_link = 'https://www.primewire.life/'
        self.key_link = '/index.php?search'
        self.moviesearch_link = '/index.php?search_keywords=%s&key=%s&search_section=1'
        self.tvsearch_link = '/index.php?search_keywords=%s&key=%s&search_section=2'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            key = urlparse.urljoin(self.base_link, self.key_link)
            key = proxy.request(key, 'main_body')
            key = client.parseDOM(key, 'input', ret='value', attrs = {'name': 'key'})[0]

            query = self.moviesearch_link % (urllib.quote_plus(cleantitle.query(title)), key)
            query = urlparse.urljoin(self.base_link, query)

            result = str(proxy.request(query, 'main_body'))
            if 'page=2' in result or 'page%3D2' in result: result += str(proxy.request(query + '&page=2', 'main_body'))

            result = client.parseDOM(result, 'div', attrs = {'class': 'index_item.+?'})

            title = 'watch' + cleantitle.get(title)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [i for i in result if any(x in i[1] for x in years)]

            r = [(proxy.parse(i[0]), i[1]) for i in result]

            match = [i[0] for i in r if title == cleantitle.get(i[1]) and '(%s)' % str(year) in i[1]]

            match2 = [i[0] for i in r]
            match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
            if match2 == []: return

            for i in match2[:5]:
                try:
                    if len(match) > 0: url = match[0] ; break
                    r = proxy.request(urlparse.urljoin(self.base_link, i), 'main_body')
                    r = re.findall('(tt\d+)', r)
                    if imdb in r: url = i ; break
                except:
                    pass

            url = re.findall('(?://.+?|)(/.+)', url)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            key = urlparse.urljoin(self.base_link, self.key_link)
            key = proxy.request(key, 'main_body')
            key = client.parseDOM(key, 'input', ret='value', attrs = {'name': 'key'})[0]
            query = self.tvsearch_link % (urllib.quote_plus(cleantitle.query(tvshowtitle)), key)
            query = urlparse.urljoin(self.base_link, query)

            result = str(proxy.request(query, 'main_body'))
            if 'page=2' in result or 'page%3D2' in result: result += str(proxy.request(query + '&page=2', 'main_body'))

            result = client.parseDOM(result, 'div', attrs = {'class': 'index_item.+?'})

            tvshowtitle = 'watch' + cleantitle.get(tvshowtitle)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [i for i in result if any(x in i[1] for x in years)]

            r = [(proxy.parse(i[0]), i[1]) for i in result]

            match = [i[0] for i in r if tvshowtitle == cleantitle.get(i[1]) and '(%s)' % str(year) in i[1]]

            match2 = [i[0] for i in r]
            match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
            if match2 == []: return

            for i in match2[:5]:
                try:
                    if len(match) > 0: url = match[0] ; break
                    r = proxy.request(urlparse.urljoin(self.base_link, i), 'main_body')
                    r = re.findall('(tt\d+)', r)
                    if imdb in r: url = i ; break
                except:
                    pass

            url = re.findall('(?://.+?|)(/.+)', url)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.urljoin(self.base_link, url)

            result = proxy.request(url, 'main_body')
            result = client.parseDOM(result, 'div', attrs = {'class': 'tv_episode_item'})

            title = cleantitle.get(title)

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'span', attrs = {'class': 'tv_episode_name'}), re.compile('(\d{4}-\d{2}-\d{2})').findall(i)) for i in result]
            result = [(i[0], i[1][0], i[2]) for i in result if len(i[1]) > 0] + [(i[0], None, i[2]) for i in result if len(i[1]) == 0]
            result = [(i[0], i[1], i[2][0]) for i in result if len(i[2]) > 0] + [(i[0], i[1], None) for i in result if len(i[2]) == 0]
            result = [(i[0][0], i[1], i[2]) for i in result if len(i[0]) > 0]

            url = [i for i in result if title == cleantitle.get(i[1]) and premiered == i[2]][:1]
            if len(url) == 0: url = [i for i in result if premiered == i[2]]
            if len(url) == 0 or len(url) > 1: url = [i for i in result if 'season-%01d-episode-%01d' % (int(season), int(episode)) in i[0]]

            url = client.replaceHTMLCodes(url[0][0])
            url = proxy.parse(url)
            url = re.findall('(?://.+?|)(/.+)', url)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = proxy.request(url, 'main_body')

            links = client.parseDOM(result, 'tbody')

            for i in links:
                try:
                    url = client.parseDOM(i, 'a', ret='href')[0]
                    url = proxy.parse(url)
                    url = urlparse.parse_qs(urlparse.urlparse(url).query)['url'][0]
                    url = base64.b64decode(url)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')

                    quality = client.parseDOM(i, 'span', ret='class')[0]
                    quality,info = source_utils.get_release_quality(quality, url)

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


