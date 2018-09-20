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

import re
import urllib
import urlparse
import json

from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import directstream
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['moviesgolds.net', 'moviesonlinegold.com']
        self.base_link = 'https://www.moviesonlinegold.com/'
        self.search_path = ('?s=%s')

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            query = ('%s-%s' % (clean_title, year))
            url = urlparse.urljoin(self.base_link, query)
            response = client.request(url)

            url = re.findall('''<a\s*href=['\"](http://www\.buzzmovie\.site/\?p=\d+)''', response)[0]

            return url
        except Exception:
            return
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
                    
            info_response = client.request(url)

            iframes = re.findall('''<iframe\s*src=['"]([^'"]+)''', info_response)

            for url in iframes:
                host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                if host in hostDict:
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': 'en',
                        'url': url.replace('\/','/'),
                        'direct': False,
                        'debridonly': False
                    })
            return sources
        except Exception:
            return

    def resolve(self, url):
        return url
