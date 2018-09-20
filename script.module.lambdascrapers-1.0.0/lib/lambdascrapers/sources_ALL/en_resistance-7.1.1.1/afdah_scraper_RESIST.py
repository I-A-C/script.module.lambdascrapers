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
import string
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES
BASE_URL = 'http://afdah.tv'

class Afdah_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'afdah'

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

            match = re.search('This movie is of poor quality', html, re.I)
            if match:
                quality = QUALITIES.LOW
            else:
                quality = QUALITIES.HIGH

            for match in re.finditer('href="([^"]+/embed\d*/[^"]+)', html):
                url = match.group(1)
                embed_html = self._http_get(url, cache_limit=.5)
                r = re.search('{\s*write\("([^"]+)', embed_html)
                if r:
                    plaintext = self._caesar(r.group(1), 13).decode('base-64')
                    if 'http' not in plaintext:
                        plaintext = self._caesar(r.group(1).decode('base-64'), 13).decode('base-64')
                else:
                    plaintext = embed_html
                hosters += self._get_links(plaintext)
            
            pattern = 'href="([^"]+)".*play_video.gif'
            for match in re.finditer(pattern, html, re.I):
                url = match.group(1)
                host = urlparse.urlparse(url).hostname
                hoster = {'multi-part': False, 'url': url, 'host': host, 'class': self, 'quality': self._get_quality(video, host, quality), 'rating': None, 'views': None, 'direct': False}
                hosters.append(hoster)
        return hosters

    def _get_links(self, html):
        hosters = []
        for match in re.finditer('file\s*:\s*"([^"]+).*?label\s*:\s*"([^"]+)', html):
            url, resolution = match.groups()
            hoster = {'multi-part': False, 'url': url, 'host': self._get_direct_hostname(url), 'class': self, 'quality': self._height_get_quality(resolution[:-1]), 'rating': None, 'views': None, 'direct': True}
            hosters.append(hoster)
        return hosters

    def _caesar(self, plaintext, shift):
        lower = string.ascii_lowercase
        lower_trans = lower[shift:] + lower[:shift]
        alphabet = lower + lower.upper()
        shifted = lower_trans + lower_trans.upper()
        return plaintext.translate(string.maketrans(alphabet, shifted))

    def get_url(self, video):
        return super(Afdah_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/wp-content/themes/afdah/ajax-search.php')
        data = {'search': title, 'type': 'title'}
        html = self._http_get(search_url, data=data, cache_limit=0)
        pattern = '<li>.*?href="([^"]+)">([^<]+)\s+\((\d{4})\)'
        results = []
        for match in re.finditer(pattern, html, re.DOTALL | re.I):
            url, title, match_year = match.groups('')
            if not year or not match_year or year == match_year:
                result = {'url': url.replace(self.base_url, ''), 'title': title, 'year': year}
                results.append(result)
        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(Afdah_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
