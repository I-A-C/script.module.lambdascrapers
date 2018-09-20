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
import json
import xbmcaddon
import xbmc
from salts_lib import log_utils
from salts_lib import dom_parser
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES
from salts_lib.constants import Q_ORDER

BASE_URL = 'https://mvsnap.com'

class Mvsnap_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'mvsnap'

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
            fragment = dom_parser.parse_dom(html, 'select', {'id': 'myDropdown'})
            if fragment:
                fragment = fragment[0]
                for match in re.finditer('<option\s+value="([^"]+)', fragment):
                    stream_url = match.group(1)
                    stream_url = urlparse.urljoin(self.base_url, stream_url)
                    stream_url = self._http_get(stream_url, allow_redirect=False, cache_limit=.5)
                    hoster = {'multi-part': False, 'host': self._get_direct_hostname(stream_url), 'class': self, 'quality': self._gv_get_quality(stream_url), 'views': None, 'rating': None, 'url': stream_url, 'direct': True}
                    hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return super(Mvsnap_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/v1/api/search?query=')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=.25)
        results = []
        if html:
            try:
                js_data = json.loads(html)
            except ValueError:
                log_utils.log('Invalid JSON returned: %s: %s' % (search_url, html), xbmc.LOGWARNING)
            else:
                if 'movies' in js_data:
                    for item in js_data['movies']:
                        if item['type'] != 'movies':
                            continue
                        
                        match = re.search('(.*)(?:\s+\((\d{4})\))', item['title'])
                        if match:
                            match_title, match_year = match.groups()
                        else:
                            match_title = item['title']
                            match_year = ''
                        
                        result = {'title': match_title, 'url': '/movies/%s' % (item['slug']), 'year': match_year}
                        results.append(result)
        return results

    def _http_get(self, url, data=None, allow_redirect=True, cache_limit=8):
        return super(Mvsnap_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, allow_redirect=allow_redirect, cache_limit=cache_limit)
