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
import xbmcaddon
import urllib
import base64
from salts_lib import dom_parser
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://clickplay.to'

class ClickPlay_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'clickplay.to'

    def resolve_link(self, link):
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

            ele = dom_parser.parse_dom(html, 'video')
            if ele:
                stream_url = dom_parser.parse_dom(ele, 'source', ret='src')
                if stream_url:
                    hoster = {'multi-part': False, 'url': stream_url[0], 'class': self, 'quality': QUALITIES.HD720, 'host': self._get_direct_hostname(stream_url[0]), 'rating': None, 'views': None, 'direct': True}
                    if hoster['host'] == 'gvideo':
                        hoster['quality'] = self._gv_get_quality(hoster['url'])
                    hosters.append(hoster)
            
            sources = dom_parser.parse_dom(html, 'iframe', ret='src')
            for src in sources:
                if 'facebook' in src: continue
                host = urlparse.urlparse(src).hostname
                hoster = {'multi-part': False, 'url': src, 'class': self, 'quality': QUALITIES.HIGH, 'host': host, 'rating': None, 'views': None, 'direct': False}
                hosters.append(hoster)
                
        return hosters

    def get_url(self, video):
        return super(ClickPlay_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        season_url = show_url + 'season-%d/' % (int(video.season))
        episode_pattern = 'href="([^"]+/season-%d/episode-%d-[^"]+)' % (int(video.season), int(video.episode))
        title_pattern = 'href="([^"]+)"\s+title="[^"]+/\s*([^"]+)'
        return super(ClickPlay_Scraper, self)._default_get_episode_url(season_url, video, episode_pattern, title_pattern)

    def search(self, video_type, title, year):
        url = urlparse.urljoin(self.base_url, '/tv-series-a-z-list')
        html = self._http_get(url, cache_limit=8)

        results = []
        pattern = '<li>\s*<a.*?href="([^"]+)[^>]*>([^<]+)'
        norm_title = self._normalize_title(title)
        for match in re.finditer(pattern, html, re.DOTALL):
            url, match_title_year = match.groups()
            r = re.search('(.*?)\s+\((\d{4})\)', match_title_year)
            if r:
                match_title, match_year = r.groups()
            else:
                match_title = match_title_year
                match_year = ''

            if norm_title in self._normalize_title(match_title) and (not year or not match_year or year == match_year):
                result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': match_year}
                results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(ClickPlay_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
