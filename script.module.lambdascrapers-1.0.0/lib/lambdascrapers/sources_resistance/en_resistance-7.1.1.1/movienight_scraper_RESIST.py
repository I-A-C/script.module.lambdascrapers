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
from salts_lib.constants import QUALITIES

BASE_URL = 'http://movienight.ws'
QUALITY_MAP = {'SD': QUALITIES.HIGH, 'HD': QUALITIES.HD720}

class MovieNight_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'MovieNight'

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

            match = re.search('Quality\s*:\s*([^<]+)', html)
            if match:
                page_quality = QUALITY_MAP.get(match.group(1), QUALITIES.HIGH)
            else:
                page_quality = QUALITIES.HIGH

            match = re.search("onClick=\"javascript:replaceb64Text.*?,\s*'([^']+)", html)
            if match:
                html = match.group(1).decode('base-64').replace('&quot;', '"')
                    
            match = re.search('iframe\s+src="([^"]+)', html)
                    
            if match:
                url = match.group(1)
                host = urlparse.urlsplit(url).hostname.lower()
                hoster = {'multi-part': False, 'host': host, 'url': url, 'class': self, 'rating': None, 'views': None, 'quality': self._get_quality(video, host, page_quality), 'direct': False}
                hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(MovieNight_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        results = []
        search_url = urlparse.urljoin(self.base_url, '/?s=%s' % (urllib.quote_plus(title)))
        html = self._http_get(search_url, cache_limit=.25)
        for match in re.finditer('class="home_post_cont.*?href="([^"]+).*?/&quot;&gt;(.*?)&lt;', html, re.DOTALL):
            link, match_title_year = match.groups()
            match = re.search('(.*?)(?:\s+\(?(\d{4})\)?)', match_title_year)
            if match:
                match_title, match_year = match.groups()
            else:
                match_title = match_title_year
                match_year = ''

            if not year or not match_year or year == match_year:
                result = {'url': link.replace(self.base_url, ''), 'title': match_title, 'year': match_year}
                results.append(result)

        return results

    def _http_get(self, url, data=None, headers=None, cache_limit=8):
        return super(MovieNight_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, headers=headers, cache_limit=cache_limit)
