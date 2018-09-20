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
import xbmc
import base64
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://zumvo.me'
QUALITY_MAP = {'HD': QUALITIES.HIGH, 'CAM': QUALITIES.LOW, 'BR-RIP': QUALITIES.HD720, 'UNKNOWN': QUALITIES.MEDIUM, 'SD': QUALITIES.HIGH}

class Zumvo_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'zumvo.com'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s (%s views)' % (item['quality'], item['host'], item['views'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=0)
            quality = QUALITIES.LOW
            match = re.search('class="status">([^<]+)', html)
            if match:
                quality = QUALITY_MAP.get(match.group(1), QUALITIES.LOW)

            views = None
            match = re.search('Views:</dt>\s*<dd>(\d+)', html, re.DOTALL)
            if match:
                views = match.group(1)

            match = re.search('href="([^"]+)"\s*class="btn-watch"', html)
            if match:
                html = self._http_get(match.group(1), cache_limit=0)
                match = re.search('proxy\.link":\s*"([^"&]+)', html)
                if match:
                    proxy_link = match.group(1)
                    proxy_link = proxy_link.split('*', 1)[-1]
                    stream_url = self._gk_decrypt(base64.urlsafe_b64decode('NlFQU1NQSGJrbXJlNzlRampXdHk='), proxy_link)
                    if 'picasa' in stream_url:
                        for source in self._parse_google(stream_url):
                            hoster = {'multi-part': False, 'url': source, 'class': self, 'quality': self._gv_get_quality(source), 'host': self._get_direct_hostname(source), 'rating': None, 'views': views, 'direct': True}
                            hosters.append(hoster)
                    else:
                        hoster = {'multi-part': False, 'url': stream_url, 'class': self, 'quality': quality, 'host': urlparse.urlsplit(stream_url).hostname, 'rating': None, 'views': views, 'direct': False}
                        hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(Zumvo_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/search/')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=0)
        results = []
        match = re.search('ul class="list-film"(.*?)</ul>', html, re.DOTALL)
        if match:
            result_fragment = match.group(1)
            pattern = 'class="name">\s*<a\s+href="([^"]+)"\s+title="Watch\s+(.*?)\s+\((\d{4})\)'
            for match in re.finditer(pattern, result_fragment, re.DOTALL):
                url, title, match_year = match.groups('')
                if not year or not match_year or year == match_year:
                    result = {'url': url.replace(self.base_url, ''), 'title': title, 'year': match_year}
                    results.append(result)
        return results

    def _http_get(self, url, cache_limit=8):
        html = super(Zumvo_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
        cookie = self._get_sucuri_cookie(html)
        if cookie:
            log_utils.log('Setting Zumvo cookie: %s' % (cookie), xbmc.LOGDEBUG)
            html = super(Zumvo_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cookies=cookie, cache_limit=0)
        return html
