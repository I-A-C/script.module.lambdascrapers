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
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES
from salts_lib import dom_parser

BASE_URL = 'http://popcorntimefree.info'

class PopcornTime_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'popcorntimefree'

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
            match = re.search('<iframe[^>]*src="([^"]+)', html)
            if match:
                stream_url = match.group(1)
                host = urlparse.urlparse(stream_url).hostname
                hoster = {'multi-part': False, 'url': stream_url, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'host': host, 'rating': None, 'views': None, 'direct': False}
                hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return super(PopcornTime_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/?query=')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=.25)
        results = []
        info = dom_parser.parse_dom(html, 'div', {'class': 'movie-info'})
        for item in info:
            match_title = dom_parser.parse_dom(item, 'span', {'class': 'movie-title'})
            match_year = dom_parser.parse_dom(item, 'span', {'class': 'movie-year'})
            if match_title:
                match_title = self.__strip_link(match_title[0])
                if match_year:
                    match_year = self.__strip_link(match_year[0])
                else:
                    match_year = ''
                    
                match = re.search('href="([^"]+)', item)
                if match:
                    url = match.group(1)
                else:
                    continue
    
                if not year or not match_year or year == match_year:
                    result = {'title': match_title, 'year': match_year, 'url': url.replace(self.base_url, '')}
                    results.append(result)

        return results

    def __strip_link(self, html):
        text = dom_parser.parse_dom(html, 'a')
        if text:
            return text[0]
        else:
            return html
    
    def _http_get(self, url, data=None, cache_limit=8):
        return super(PopcornTime_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
