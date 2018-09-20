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
import xbmc
import urllib
import urlparse
import re
import xbmcaddon
import random
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES
from salts_lib.constants import USER_AGENT

QUALITY_MAP = {'HD': QUALITIES.HIGH, 'LOW': QUALITIES.LOW}
BASE_URL = 'http://twomovies.us'
UA_RAND = {
           'Mozilla/5.0': ['Mozilla/5.0', 'Mozilla/4.0'],
           'MSIE 11': ['MSIE 11', 'MSIE 11.0', 'MSIE 10.0', 'MSIE 9.0', 'MSIE 8.0', 'MSIE 7.0b', 'MSIE 7.0'],
           'Windows NT 6.3': ['Windows NT 6.3', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.0', 'Windows 3.1'],
           'Trident/7.0': ['Trident/7.0', 'Trident/6.0', 'Trident/5.0', 'Trident/4.0']
           }

class TwoMovies_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return '2movies'

    def resolve_link(self, link):
        url = urlparse.urljoin(self.base_url, link)
        html = self._http_get(url, cookies={'links_tos': '1'}, cache_limit=0)
        match = re.search('<iframe[^<]+src=(?:"|\')([^"\']+)', html, re.DOTALL | re.I)
        if match:
            return match.group(1)

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        sources = []
        source_url = self.get_url(video)
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=1)

            pattern = 'class="playDiv3".*?href="([^"]+).*?>(.*?)</a>'
            for match in re.finditer(pattern, html, re.DOTALL | re.I):
                url, host = match.groups()
                source = {'multi-part': False, 'url': url.replace(self.base_url, ''), 'host': host, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'rating': None, 'views': None, 'direct': False}
                sources.append(source)
        return sources

    def get_url(self, video):
        return super(TwoMovies_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/search/?criteria=title&order=year&sort=desc&search_query=')
        search_url += urllib.quote_plus(title.lower())
        html = self._http_get(search_url, cache_limit=0)
        results = []

        # filter the html down to only tvshow or movie results
        if video_type in [VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE]:
            pattern = '<h1>Tv Shows</h1>.*'
        else:
            pattern = '<div class="filmDiv".*(<h1>Tv Shows</h1>)*'
        match = re.search(pattern, html, re.DOTALL)
        try:
            if match:
                fragment = match.group(0)
                pattern = 'href="([^"]+)" class="filmname">(.*?)\s*</a>.*?/all/byViews/(\d+)/'
                for match in re.finditer(pattern, fragment, re.DOTALL):
                    result = {}
                    url, res_title, res_year = match.groups('')
                    if not year or year == res_year:
                        result['title'] = res_title
                        result['url'] = url.replace(self.base_url, '')
                        result['year'] = res_year
                        results.append(result)
        except Exception as e:
            log_utils.log('Failure during %s search: |%s|%s|%s| (%s)' % (self.get_name(), video_type, title, year, str(e)), xbmc.LOGWARNING)

        return results

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'class="linkname\d*" href="([^"]+/watch_episode/[^/]+/%s/%s/)"' % (video.season, video.episode)
        title_pattern = 'class="linkname"\s+href="([^"]+)">Episode_\d+\s+-\s+([^<]+)'
        return super(TwoMovies_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern)

    def _http_get(self, url, cookies=None, cache_limit=8):
        user_agent = USER_AGENT
        for key in UA_RAND:
            user_agent = user_agent.replace(key, random.choice(UA_RAND[key]))
        headers = {'User-Agent': user_agent}
        return super(TwoMovies_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cookies, headers=headers, cache_limit=cache_limit)
