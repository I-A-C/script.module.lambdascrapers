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
import scraper
import urllib
import urlparse
import re
import xbmcaddon
from salts_lib import dom_parser
from salts_lib.constants import VIDEO_TYPES

BASE_URL = 'http://xmovies8.tv'

class XMovies8_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'xmovies8'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            for match in re.finditer('href="([^"]+)[^>]*>(\d+)x(\d+)', html):
                stream_url, width, _ = match.groups()
                hoster = {'multi-part': False, 'host': self._get_direct_hostname(stream_url), 'class': self, 'quality': self._width_get_quality(width), 'views': None, 'rating': None, 'url': stream_url, 'direct': True}
                hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return super(XMovies8_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/?s=%s' % urllib.quote_plus(title))
        html = self._http_get(search_url, cache_limit=.25)
        results = []
        for result in dom_parser.parse_dom(html, 'h2'):
            match = re.search('href="([^"]+)"[^>]*>([^<]+)', result)
            if match:
                url, match_title_year = match.groups()
                match = re.search('(.*?)\s+\((\d{4})\)', match_title_year)
                if match:
                    match_title, match_year = match.groups()
                else:
                    match_title = match_title_year
                    match_year = ''

                if not year or not match_year or year == match_year:
                    result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': match_year}
                    results.append(result)
        return results

    def _http_get(self, url, cookies=None, data=None, cache_limit=8):
        return super(XMovies8_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cookies=cookies, data=data, cache_limit=cache_limit)
