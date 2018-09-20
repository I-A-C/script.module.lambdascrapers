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
import json
import xml.dom.minidom
from salts_lib.constants import VIDEO_TYPES
from salts_lib import log_utils

BASE_URL = 'http://www.hdmoviezone.net'
PHP_URL = 'http://gl.hdmoviezone.net/hdmzgl.php'
COOKIE_URL = 'http://gl.hdmoviezone.net/getimage.php'

class hdmz_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'hdmz'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            _html = self._http_get(COOKIE_URL, cache_limit=.25)
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            match = re.search('file\s*=\s*"([^"]+)', html)
            if match:
                file_hash = match.group(1)
                data = self._http_get(PHP_URL, data={'url': file_hash}, headers={'Origin': self.base_url, 'Referer': source_url}, cache_limit=0)
                if data:
                    try:
                        js_data = json.loads(data)
                    except ValueError:
                        log_utils.log('No JSON returned: %s: %s' % (url, data), xbmc.LOGWARNING)
                    else:
                        if js_data and 'content' in js_data:
                            for item in js_data['content']:
                                if 'type' in item and item['type'].lower().startswith('video'):
                                    hoster = {'multi-part': False, 'host': self._get_direct_hostname(item['url']), 'url': item['url'], 'class': self, 'rating': None, 'views': None, 'quality': self._width_get_quality(item['width']), 'direct': True}
                                    hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(hdmz_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        results = []
        search_url = urlparse.urljoin(self.base_url, '/feed/?s=%s&paged=1' % (urllib.quote_plus(title)))
        data = self._http_get(search_url, cache_limit=.25)
        dom = xml.dom.minidom.parseString(data)
        for item in dom.getElementsByTagName('item'):
            title_year = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8')
            link = item.getElementsByTagName('link')[0].firstChild.data.encode('utf-8')
            match = re.search('(.*)\s+\((\d{4})\)', title_year)
            if match:
                match_title, match_year = match.groups()
            else:
                match_title = title_year
                match_year = ''

            if not year or not match_year or year == match_year:
                result = {'url': link.replace(self.base_url, ''), 'title': match_title, 'year': match_year}
                results.append(result)

        return results

    def _http_get(self, url, data=None, headers=None, cache_limit=8):
        return super(hdmz_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, headers=headers, cache_limit=cache_limit)
