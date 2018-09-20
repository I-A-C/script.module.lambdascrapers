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
import base64
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

QUALITY_MAP = {'DVD': QUALITIES.HIGH, 'CAM': QUALITIES.LOW}
BASE_URL = 'http://movie25.ag'

class Movie25_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'movie25'

    def resolve_link(self, link):
        url = urlparse.urljoin(self.base_url, link)
        html = self._http_get(url, cache_limit=0)
        match = re.search('href=\'([^\']*)\'"\s+value="Click Here to Play"', html, re.DOTALL | re.I)
        if match:
            return match.group(1)
        else:
            match = re.search('<IFRAME SRC="(?:/?tz\.php\?url=external\.php\?url=)?([^"]+)', html, re.DOTALL | re.I)
            if match:
                try:
                    return base64.b64decode(match.group(1))
                except TypeError:
                    return match.group(1)
            else:
                return link

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)

            quality = None
            match = re.search('Links\s+-\s+Quality\s*([^<]*)</h1>', html, re.DOTALL | re.I)
            if match:
                quality = QUALITY_MAP.get(match.group(1).strip().upper())

            for match in re.finditer('id="link_name">\s*([^<]+).*?href="([^"]+)', html, re.DOTALL):
                host, url = match.groups()
                host = host.lower().strip()
                hoster = {'multi-part': False, 'host': host, 'class': self, 'url': url, 'quality': self._get_quality(video, host, quality), 'rating': None, 'views': None, 'direct': False}
                hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return super(Movie25_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/search.php?key=')
        search_url += urllib.quote_plus('%s %s' % (title, year))
        search_url += '&submit='
        html = self._http_get(search_url, cache_limit=.25)
        pattern = 'class="movie_about">.*?href="([^"]+).*?>\s+(.*?)\s*\(?(\d{4})?\)?\s+</a></h1>'
        results = []
        for match in re.finditer(pattern, html, re.DOTALL):
            url, title, year = match.groups('')
            result = {'url': url, 'title': title, 'year': year}
            results.append(result)
        return results

    def _http_get(self, url, cache_limit=8):
        return super(Movie25_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
