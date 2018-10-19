

# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Yoda
# Addon id: plugin.video.Yoda
# Addon Provider: MuadDib

import re,traceback,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['xmovies8.tv', 'xmovies8.ru', 'xmovies8.es']
        self.base_link = 'https://xmovies8.es'
        self.search_link = 'https://search.' + self.domains[2] +'/?q=%s&page=1'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('XMovies - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('XMovies - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('XMovies - Exception: \n' + str(failure))
            return

    def searchShow(self, title, season, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)

            url = self.search_link % urllib.quote_plus('%s Season %01d' % (title, int(season)))
            r = client.request(url)

            r = client.parseDOM(r, 'div', attrs={'class': 'item_movie'})[0]

            if r:
                url = client.parseDOM(r, 'a', ret='href')[0]
                url = re.sub(r'\/\/xmovies8\.es', '', url)
            # if sr:
            #     r = client.parseDOM(sr, 'h2', attrs={'class': 'tit'})
            #     r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in r]
            #     r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            #     r = [(i[0], re.findall('(.+?)\s+-\s+S(\d+)', i[1])) for i in r]
            #     r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if len(i[1]) > 0]
            #     r = [i[0] for i in r if t == cleantitle.get(i[1]) and int(season) == int(i[2])][0]
            # else:
            #     url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.query('%s Season %01d' % (title.replace('\'', '-'), int(season)))))
            #     sr = client.request(url, headers=headers, timeout='10')
            #     if sr:
            #         r = client.parseDOM(sr, 'h2', attrs={'class': 'tit'})
            #         r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in r]
            #         r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            #         r = [(i[0], re.findall('(.+?)\s+-\s+Season\s+(\d+)', i[1])) for i in r]
            #         r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if len(i[1]) > 0]
            #         r = [i[0] for i in r if t == cleantitle.get(i[1]) and int(season) == int(i[2])][0]
            #     else:
            #         url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.query('%s %01d' % (title.replace('\'', '-'), int(year)))))
            #         sr = client.request(url, headers=headers, timeout='10')
            #         if sr:
            #             r = client.parseDOM(sr, 'h2', attrs={'class': 'tit'})
            #             r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in r]
            #             r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            #             r = [(i[0], re.findall('(.+?) \((\d{4})', i[1])) for i in r]
            #             r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if len(i[1]) > 0]
            #             r = [i[0] for i in r if t == cleantitle.get(i[1]) and year == i[2]][0]
            # url = re.findall('(?://.+?|)(/.+)', r)[0]
            # url = client.replaceHTMLCodes(url)
            #
            # return url.encode('utf-8')

            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('XMovies - Exception: \n' + str(failure))
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            url = urlparse.urljoin(self.base_link, self.search_link % (cleantitle.geturl(title.replace('\'', '-'))))
            r = client.request(url, timeout='10', headers=headers)
            r = client.parseDOM(r, 'h2', attrs={'class': 'tit'})
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in r]
            r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [(i[0], re.findall('(.+?) \((\d{4})', i[1])) for i in r]
            r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if len(i[1]) > 0]
            try:
                match = [i[0] for i in r if self.matchAlias(i[1], aliases) and year == i[2]][0]
            except:
                match = [i[0] for i in r if self.matchAlias(i[1], aliases)][0]

            url = re.findall('(?://.+?|)(/.+)', match)[0]
            url = client.replaceHTMLCodes(url)
            return url.encode('utf-8')
        except:
            failure = traceback.format_exc()
            log_utils.log('XMovies - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                episode = int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], data['year'], aliases, headers)
            else:
                episode = 0
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            url = re.sub('/watching.html$', '', url.strip('/'))
            url = url + '/watching.html'

            p = client.request(url)

            if episode > 0:
                r = client.parseDOM(p, 'div', attrs={'class': 'ep_link.+?'})[0]
                r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a'))
                r = [(i[0], re.findall('Episode\s+(\d+)', i[1])) for i in r]
                r = [(i[0], i[1][0]) for i in r]
                url = [i[0] for i in r if int(i[1]) == episode][0]
                p = client.request(url, headers=headers, timeout='10')

            referer = url

            id = re.findall('load_player\(.+?(\d+)', p)[0]
            r = urlparse.urljoin(self.base_link, '/ajax/movie/load_player_v3?id=%s' % id)
            r = client.request(r, referer=referer, XHR=True)

            url = json.loads(r)['value']

            if (url.startswith('//')):
                url = 'https:' + url

            r = client.request(url, referer=referer, XHR=True)

            headers = {
                'User-Agent': client.randomagent(),
                'Referer': referer
            }

            headers = '|' + urllib.urlencode(headers)

            source = str(json.loads(r)['playlist'][0]['file']) + headers

            sources.append({'source': 'CDN', 'quality': 'HD', 'language': 'en', 'url': source, 'direct': True, 'debridonly': False})

            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('XMovies - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url