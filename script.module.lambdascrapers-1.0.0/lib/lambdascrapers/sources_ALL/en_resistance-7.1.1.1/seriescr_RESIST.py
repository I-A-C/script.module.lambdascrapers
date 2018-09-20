# -*- coding: UTF-8 -*-
#           ________
#          _,.-Y  |  |  Y-._
#      .-~"   ||  |  |  |   "-.
#      I" ""=="|" !""! "|"[]""|     _____
#      L__  [] |..------|:   _[----I" .-{"-.
#     I___|  ..| l______|l_ [__L]_[I_/r(=}=-P
#    [L______L_[________]______j~  '-=c_]/=-^
#     \_I_j.--.\==I|I==_/.--L_]
#       [_((==)[`-----"](==)j
#          I--I"~~"""~~"I--I
#          |[]|         |[]|
#          l__j         l__j
#         |!!|         |!!|
#          |..|         |..|
#          ([])         ([])
#          ]--[         ]--[
#          [_L]         [_L]
#         /|..|\       /|..|\
#        `=}--{='     `=}--{='
#       .-^--r-^-.   .-^--r-^-.
# Resistance is futile @lock_down... 

import re,traceback,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import debrid
from resources.lib.modules import dom_parser2
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['seriescr.com']
        self.base_link = 'http://seriescr.com/'
        self.search_link = '/search/%s/feed/rss2/'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('SeriesCR - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('SeriesCR - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode']))
            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            url = self.search_link % urllib.quote_plus(query)
            r = urlparse.urljoin(self.base_link, url)
            r = client.request(r)
            r = client.parseDOM(r, 'item')
            title = client.parseDOM(r, 'title')[0]
            if hdlr in title:
                r = re.findall('<h3.+?>(.+?)</h3>\s*<h5.+?<strong>(.+?)</strong.+?h3.+?adze.+?href="(.+?)">.+?<h3', r[0], re.DOTALL)
                for name, size, url in r:
                    quality, info = source_utils.get_release_quality(name, url)
                    try:
                        size = re.sub('i', '', size)
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except:
                        pass

                    info = ' | '.join(info)

                    valid, host = source_utils.is_host_valid(url, hostDict)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('SeriesCR - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url


