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
from salts_lib.constants import QUALITIES

BASE_URL = 'http://ayyex.com'
QUALITY_MAP = {'HD': QUALITIES.HD720, 'FULL HD': QUALITIES.HD1080, 'DVD': QUALITIES.MEDIUM}

class Ayyex_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'ayyex'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        label = '[%s] %s' % (item['quality'], item['host'])
        if 'views' in item and item['views']:
            label += ' (%s views)' % item['views']
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            fragment = dom_parser.parse_dom(html, 'div', {'id': 'player2'})
            if fragment:
                for match in re.finditer('<iframe[^>]*src="([^"]+)', fragment[0], re.I):
                    stream_url = match.group(1)
                    host = urlparse.urlparse(stream_url).hostname
                    hoster = {'multi-part': False, 'host': host, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'views': None, 'rating': None, 'url': stream_url, 'direct': False}
                    hosters.append(hoster)
            
        return hosters

    def get_url(self, video):
        return super(Ayyex_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        results = []
        search_url = urlparse.urljoin(self.base_url, '/?s=%s')
        search_url = search_url % (urllib.quote_plus(title))
        html = self._http_get(search_url, cache_limit=0)
        norm_title = self._normalize_title(title)
        for item in dom_parser.parse_dom(html, 'div', {'class': 'item'}):
            match = re.search('href="([^"]+).*?<h2>([^<]+).*?class="year">\s*(\d+)', item, re.DOTALL)
            if match:
                url, match_title, match_year = match.groups('')
                if norm_title in self._normalize_title(match_title) and (not year or not match_year or year == match_year):
                    result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': match_year}
                    results.append(result)
                
        
        return results

    def _http_get(self, url, cache_limit=8):
        return super(Ayyex_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
