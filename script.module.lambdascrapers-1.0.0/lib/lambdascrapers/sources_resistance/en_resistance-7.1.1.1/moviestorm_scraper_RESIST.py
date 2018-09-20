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
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES
from salts_lib import dom_parser

BASE_URL = 'http://moviestorm.eu'
QUALITY_MAP = {'HD': QUALITIES.HIGH, 'CAM': QUALITIES.LOW, 'BRRIP': QUALITIES.HIGH, 'UNKNOWN': QUALITIES.MEDIUM, 'DVDRIP': QUALITIES.HIGH}

class MovieStorm_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'moviestorm.eu'

    def resolve_link(self, link):
        if self.base_url in link:
            url = urlparse.urljoin(self.base_url, link)
            html = self._http_get(url, cache_limit=.5)
            match = re.search('class="real_link"\s+href="([^"]+)', html)
            if match:
                return match.group(1)
        else:
            return link

    def format_source_label(self, item):
        label = '[%s] %s (%s views)' % (item['quality'], item['host'], item['views'])
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            pattern = 'class="source_td">\s*<img[^>]+>\s*(.*?)\s*-\s*\((\d+) views\).*?class="quality_td">\s*(.*?)\s*<.*?href="([^"]+)'
            for match in re.finditer(pattern, html, re.DOTALL):
                host, views, quality_str, stream_url = match.groups()

                hoster = {'multi-part': False, 'host': host.lower(), 'class': self, 'url': stream_url, 'quality': self._get_quality(video, host, QUALITY_MAP.get(quality_str.upper())), 'views': views, 'rating': None, 'direct': False}
                hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return super(MovieStorm_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'class="number left".*?href="([^"]+season-%d/episode-%d[^"]+)' % (int(video.season), int(video.episode))
        title_pattern = 'class="name left".*?href="([^"]+)">([^<]+)'
        airdate_pattern = 'class="edate[^>]+>\s*{p_month}-{p_day}-{year}.*?href="([^"]+)'
        return super(MovieStorm_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern, airdate_pattern)

    def search(self, video_type, title, year):
        results = []
        if video_type == VIDEO_TYPES.TVSHOW:
            url = urlparse.urljoin(self.base_url, '/series/all/')
            html = self._http_get(url, cache_limit=8)
    
            links = dom_parser.parse_dom(html, 'a', {'class': 'underilne'}, 'href')
            titles = dom_parser.parse_dom(html, 'a', {'class': 'underilne'})
            items = zip(links, titles)
        else:
            url = urlparse.urljoin(self.base_url, '/search?q=%s&go=Search' % urllib.quote_plus(title))
            data = {'q': title, 'go': 'Search'}
            html = self._http_get(url, data=data, cache_limit=8)
            pattern = 'class="movie_box.*?href="([^"]+).*?<h1>([^<]+)'
            items = re.findall(pattern, html)

        norm_title = self._normalize_title(title)
        for item in items:
            url, match_title = item
            if norm_title in self._normalize_title(match_title):
                result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': ''}
                results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(MovieStorm_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
