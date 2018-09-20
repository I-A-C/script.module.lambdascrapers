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
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

QUALITY_MAP = {'HD': QUALITIES.HIGH, 'LOW': QUALITIES.LOW}
BASE_URL = 'http://www.watchfree.to'

class WatchFree_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'WatchFree.to'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        sources = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)

            pattern = 'href="[^"]+gtfo=([^"]+)[^>]+>([^<]+)'
            for match in re.finditer(pattern, html, re.DOTALL | re.I):
                url, link_name = match.groups()
                url = url.decode('base-64')
                host = urlparse.urlsplit(url).hostname.lower()
                match = re.search('Part\s+(\d+)', link_name)
                if match:
                    if match.group(1) == '2':
                        del sources[-1]  # remove Part 1 previous link added
                    continue
                
                source = {'multi-part': False, 'url': url, 'host': host, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'views': None, 'rating': None, 'direct': False}
                sources.append(source)

        return sources

    def get_url(self, video):
        return super(WatchFree_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        if video_type == VIDEO_TYPES.MOVIE:
            section = '1'
            url_marker = '-movie-online-'
        else:
            section = '2'
            url_marker = '-tv-show-online-'
        search_url = urlparse.urljoin(self.base_url, '/?keyword=%s&search_section=%s' % (urllib.quote_plus(title), section))
        html = self._http_get(search_url, cache_limit=.25)

        results = []
        for match in re.finditer('class="item".*?href="([^"]+)"\s*title="Watch (.*?)(?:\s+\((\d{4})\))?"', html):
            url, res_title, res_year = match.groups('')
            if url_marker in url and (not year or not res_year or year == res_year):
                result = {'title': res_title, 'url': url.replace(self.base_url, ''), 'year': res_year}
                results.append(result)
        return results

    def _get_episode_url(self, show_url, video):
        episode_pattern = '"tv_episode_item">[^>]+href="([^"]+/season-%s-episode-%s)">' % (video.season, video.episode)
        title_pattern = 'class="tv_episode_item".*?href="([^"]+).*?class="tv_episode_name">\s+([^<]+)'
        airdate_pattern = 'class="tv_episode_item">\s*<a\s+href="([^"]+)(?:[^<]+<){5}span\s+class="tv_num_versions">{month_name} {day} {year}'
        return super(WatchFree_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern, airdate_pattern)

    def _http_get(self, url, cache_limit=8):
        return super(WatchFree_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
