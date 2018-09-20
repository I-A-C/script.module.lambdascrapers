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

BASE_URL = 'http://moviesonline7.co'
BUY_VIDS_URL = '/includes/buyVidS.php?vid=%s&num=%s'
QUALITY_MAP = {'BRRIP1': QUALITIES.HIGH, 'BRRIP2': QUALITIES.HD720, 'BRRIP3': QUALITIES.MEDIUM, 'BRRIP4': QUALITIES.HD720,
             'DVDRIP1': QUALITIES.HIGH, 'DVDRIP2': QUALITIES.HIGH, 'DVDRIP3': QUALITIES.HIGH,
             'CAM1': QUALITIES.LOW, 'CAM2': QUALITIES.LOW}

class MO7_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'MoviesOnline7'

    def resolve_link(self, link):
        html_url = self._http_get(link, cache_limit=.5)
        if html_url:
            html = self._http_get(html_url, cache_limit=.5)
            match = re.search("'file'\s*,\s*'([^']+)", html)
            if match:
                host = urlparse.urlparse(html_url).hostname
                stream_url = 'http://' + host + match.group(1)
                return stream_url

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)

            quality = QUALITIES.HIGH
            match = re.search("kokybe;([^']+)", html)
            if match:
                quality = QUALITY_MAP.get(match.group(1).upper(), QUALITIES.HIGH)

            match = re.search("buyVid\('(\d+)", html)
            if match:
                vid_num = match.group(1)
                match = re.search('n(\d+)\.html', source_url)
                if match:
                    stream_url = urlparse.urljoin(self.base_url, BUY_VIDS_URL % (match.group(1), vid_num))
                    if stream_url:
                        hoster = {'multi-part': False, 'host': self._get_direct_hostname(stream_url), 'url': stream_url, 'class': self, 'rating': None, 'views': None, 'quality': quality, 'direct': True}
                        hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(MO7_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        results = []
        search_url = urlparse.urljoin(self.base_url, '/search.php?stext=')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=.25)
        pattern = "class='bekas'.*?href='([^']+).*?color:orange.*?[^>]+>([^<]+).*?Premiere:.*?(\d{4})</a>"
        for match in re.finditer(pattern, html, re.DOTALL):
            url, match_title, match_year = match.groups('')
            if not year or not match_year or year == match_year:
                result = {'url': '/' + url, 'title': match_title, 'year': match_year}
                results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(MO7_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
