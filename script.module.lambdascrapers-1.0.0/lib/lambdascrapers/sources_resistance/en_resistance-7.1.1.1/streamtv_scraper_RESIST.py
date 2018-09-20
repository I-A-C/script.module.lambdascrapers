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
from salts_lib.constants import VIDEO_TYPES

BASE_URL = 'http://stream-tv1.net'
BASE_EP_URL = 'http://stream-tv-series.net'

class StreamTV_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'stream-tv.co'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        label = '[%s] %s ' % (item['quality'], item['host'])
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(BASE_EP_URL, source_url)
            html = self._http_get(url, cache_limit=.5)

            for match in re.finditer('postTabs_titles.*?iframe.*?src="([^"]+)', html, re.I | re.DOTALL):
                stream_url = match.group(1)
                host = urlparse.urlparse(stream_url).hostname.lower()
                hoster = {'multi-part': False, 'host': host, 'class': self, 'url': stream_url, 'quality': self._get_quality(video, host, None), 'views': None, 'rating': None, 'direct': False}
                hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(StreamTV_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href="([^"]+s%d-?e%d[^"]+)' % (int(video.season), int(video.episode))
        title_pattern = 'href="([^"]+)"\s+rel="nofollow.*</a>([^<]+)'
        ep_url = super(StreamTV_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern)
        if ep_url:
            return ep_url.replace(BASE_EP_URL, '')

    def search(self, video_type, title, year):
        url = self.base_url
        html = self._http_get(url, cache_limit=8)

        results = []
        norm_title = self._normalize_title(title)
        pattern = 'li><a\s+href="([^"]+)">([^<]+)'
        for match in re.finditer(pattern, html):
            url, match_title = match.groups()
            if norm_title in self._normalize_title(match_title):
                result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': ''}
                results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(StreamTV_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
