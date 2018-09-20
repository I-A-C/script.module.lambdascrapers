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
from salts_lib.constants import QUALITIES

BASE_URL = 'http://projectfreetv.so'

class PFTV_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'pftv'

    def resolve_link(self, link):
        url = urlparse.urljoin(self.base_url, link)
        html = self._http_get(url, cache_limit=.5)
        match = re.search('href="([^"]+).*?value="Continue to video"', html)
        if match:
            return match.group(1)
        else:
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

            for match in re.finditer('<td>\s*<a\s+href="([^"]+)(?:[^>]+>){2}\s*(?:&nbsp;)*\s*([^<]+)', html):
                url, host = match.groups()
                hoster = {'multi-part': False, 'host': host, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'views': None, 'rating': None, 'url': url.replace(self.base_url, ''), 'direct': False}
                hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(PFTV_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        url = urlparse.urljoin(self.base_url, show_url)
        html = self._http_get(url, cache_limit=8)
        season_pattern = 'href="([^"]+season-%s/)' % (video.season)
        match = re.search(season_pattern, html)
        if match:
            season_url = match.group(1)
            episode_pattern = 'href="([^"]+season-%s-episode-%s/)' % (video.season, video.episode)
            airdate_pattern = '{day} {short_month} {year}\s*<a\s+href="([^"]+)'
            return super(PFTV_Scraper, self)._default_get_episode_url(season_url, video, episode_pattern, airdate_pattern=airdate_pattern)

    def search(self, video_type, title, year):
        url = urlparse.urljoin(self.base_url, '/watch-tv-series')
        html = self._http_get(url, cache_limit=8)
        results = []
        norm_title = self._normalize_title(title)
        pattern = 'li>\s*<a\s+title="([^"]+)"\s+href="([^"]+)'
        for match in re.finditer(pattern, html):
            match_title, url = match.groups()
            if norm_title in self._normalize_title(match_title):
                result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': ''}
                results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(PFTV_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
