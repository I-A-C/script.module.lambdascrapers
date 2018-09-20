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

BASE_URL = 'http://filmikz.ch'

class Filmikz_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'filmikz.ch'

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

            pattern = "/watch\.php\?q=([^']+)"
            seen_hosts = {}
            for match in re.finditer(pattern, html, re.DOTALL):
                url = match.group(1)
                hoster = {'multi-part': False, 'url': url.decode('base-64'), 'class': self, 'quality': None, 'views': None, 'rating': None, 'direct': False}
                hoster['host'] = urlparse.urlsplit(hoster['url']).hostname
                # top list is HD, bottom list is SD
                if hoster['host'] in seen_hosts:
                    quality = QUALITIES.HIGH
                else:
                    quality = QUALITIES.HD720
                    seen_hosts[hoster['host']] = True
                hoster['quality'] = self._get_quality(video, hoster['host'].lower(), quality)
                hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return super(Filmikz_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/index.php?search=%s&image.x=0&image.y=0')
        search_url = search_url % (urllib.quote_plus(title))
        html = self._http_get(search_url, cache_limit=.25)

        results = []
        # Are we on a results page?
        if not re.search('window\.location', html):
            pattern = 'href="(/watch[^"]+)".*?<strong>(.*?)\s*\((\d{4})\)\s*:\s*</strong>'
            for match in re.finditer(pattern, html, re.DOTALL):
                url, title, match_year = match.groups('')
                if not year or not match_year or year == match_year:
                    result = {'url': url, 'title': title, 'year': match_year}
                    results.append(result)
        else:
            match = re.search('window\.location\s+=\s+"([^"]+)', html)
            if match:
                url = match.group(1)
                if url != 'movies.php':
                    result = {'url': url.replace(self.base_url, ''), 'title': title, 'year': year}
                    results.append(result)
        return results

    def _http_get(self, url, cache_limit=8):
        return super(Filmikz_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
