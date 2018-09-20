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
import re
import urlparse
import urllib
import xbmcaddon
from salts_lib import dom_parser
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://watch8now.so'

class Watch8Now_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'Watch8Now'

    def resolve_link(self, link):
        html = self._http_get(link, cache_limit=.5)
        match = re.search('<iframe[^>]*src="([^"]+)', html, re.I)
        if match:
            return match.group(1)
        else:
            match = re.search('Nothing in HERE<br>([^<]+)', html, re.I)
            if match:
                return match.group(1).strip()
        
        return link

    def format_source_label(self, item):
        label = '[%s] %s ' % (item['quality'], item['host'])
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
    
            for table_cell in dom_parser.parse_dom(html, 'td', {'class': 'domain'}):
                match = re.search('href="([^"]+)(?:[^>]+>){2}\s*([^<]+)', table_cell)
                if match:
                    link, host = match.groups()
                    hoster = {'multi-part': False, 'host': host, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'views': None, 'rating': None, 'url': link, 'direct': False}
                    hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(Watch8Now_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href="([^"]+[sS]%s[eE]%s\.html)"' % (video.season, video.episode)
        title_pattern = 'href="([^"]+[sS]\d+[eE]\d+\.html")(?:[^>]+>){6}([^<]+)'
        return super(Watch8Now_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/search?q=')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=8)
        results = []
        for item in dom_parser.parse_dom(html, 'h4', {'class': 'media-heading'}):
            match = re.search('href="([^"]+)">([^<]+)', item)
            if match:
                url, match_title = match.groups()
                result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': ''}
                results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(Watch8Now_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
