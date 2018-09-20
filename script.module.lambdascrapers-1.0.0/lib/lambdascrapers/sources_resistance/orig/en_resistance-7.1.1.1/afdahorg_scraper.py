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
from salts_lib.constants import VIDEO_TYPES

BASE_URL = 'https://afdah.org'
INFO_URL = BASE_URL + '/video_info'

class AfdahOrg_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'afdah.org'

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
            match = re.search('var\s*video_id="([^"]+)', html)
            if match:
                video_id = match.group(1)
                data = {'video_id': video_id}
                html = self._http_get(INFO_URL, data=data, cache_limit=0)
                sources = self.__parse_fmt(html)
                for width in sources:
                    hoster = {'multi-part': False, 'host': self._get_direct_hostname(sources[width]), 'class': self, 'quality': self._width_get_quality(width), 'views': None, 'rating': None, 'url': sources[width], 'direct': True}
                    hosters.append(hoster)
        return hosters

    def __parse_fmt(self, js_data):
        urls = {}
        formats = {}
        for match in re.finditer('&?([^=]+)=([^&$]+)', js_data):
            key, value = match.groups()
            value = urllib.unquote(value)
            if key == 'fmt_stream_map':
                items = value.split(',')
                for item in items:
                    source_fmt, source_url = item.split('|')
                    urls[source_url] = source_fmt
            elif key == 'fmt_list':
                items = value.split(',')
                for item in items:
                    format_key, q_str, _ = item.split('/', 2)
                    w, _ = q_str.split('x')
                    formats[format_key] = int(w)
                    
        sources = {}
        for url in urls:
            if urls[url] in formats:
                width = formats[urls[url]]
                sources[width] = url
        return sources

    def get_url(self, video):
        return super(AfdahOrg_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/results?q=')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=.25)
        results = []
        pattern = 'class="video_title".*?href="([^"]+)">([^<]+).*?Year</b>:\s*(\d*)'
        for match in re.finditer(pattern, html, re.DOTALL):
            url, match_title, match_year = match.groups()
            if not year or not match_year or year == match_year:
                result = {'title': match_title, 'year': match_year, 'url': url.replace(self.base_url, '')}
                results.append(result)
        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(AfdahOrg_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
