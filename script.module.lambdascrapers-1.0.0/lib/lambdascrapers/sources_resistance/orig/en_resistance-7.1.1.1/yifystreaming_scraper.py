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
import base64
import xbmcaddon
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib import dom_parser

BASE_URL = 'http://yify-streaming.com'
CATEGORIES = {VIDEO_TYPES.MOVIE: 'category-movies', VIDEO_TYPES.EPISODE: 'category-tv-series'}

class YifyStreaming_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'yify-streaming'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            match = re.search('href="([^"]+)">HTML Player<', html)
            if match:
                link = match.group(1)
                link = link.replace('#038;', '')
                html = self._http_get(link, cache_limit=.5)
                for match in re.finditer('<source\s+src="([^"]+)', html):
                    stream_url = match.group(1)
                    hoster = {'multi-part': False, 'url': stream_url, 'class': self, 'quality': self._gv_get_quality(stream_url), 'host': self._get_direct_hostname(stream_url), 'rating': None, 'views': None, 'direct': True}
                    hosters.append(hoster)
        return hosters

    def get_url(self, video):
        self.create_db_connection()
        url = None

        if video.video_type == VIDEO_TYPES.MOVIE:
            result = self.db_connection.get_related_url(video.video_type, video.title, video.year, self.get_name())
            if result:
                url = result[0][0]
                log_utils.log('Got local related url: |%s|%s|%s|%s|%s|' % (video.video_type, video.title, video.year, self.get_name(), url))
            else:
                results = self.search(video.video_type, video.title, video.year)
                if results:
                    url = results[0]['url']
        else:
            result = self.db_connection.get_related_url(video.video_type, video.title, video.year, self.get_name(), video.season, video.episode)
            if result:
                url = result[0][0]
                log_utils.log('Got local related url: |%s|%s|%s|' % (video, self.get_name(), url))
            else:
                url = self._get_episode_url('', video)
                if url:
                    self.db_connection.set_related_url(VIDEO_TYPES.EPISODE, video.title, video.year, self.get_name(), url, video.season, video.episode)

        return url

    def _get_episode_url(self, show_url, video):
        search_title = '%s Season %d Episode %d' % (video.title, int(video.season), int(video.episode))
        results = self.search(video.video_type, search_title, '')
        if results:
            return results[0]['url']
    
    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/?s=')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=.25)
            
        elements = dom_parser.parse_dom(html, 'li', {'class': '[^"]*%s[^"]*' % (CATEGORIES[video_type])})
        results = []
        for element in elements:
            match = re.search('href="([^"]+)[^>]+>\s*([^<]+)', element, re.DOTALL)
            if match:
                url, match_title_year = match.groups()
                match = re.search('(.*?)(?:\s+\(?(\d{4})\)?)', match_title_year)
                if match:
                    match_title, match_year = match.groups()
                else:
                    match_title = match_title_year
                    match_year = ''
                
                if not year or not match_year or year == match_year:
                    result = {'title': match_title, 'year': match_year, 'url': url.replace('https', 'http').replace(self.base_url, '')}
                    results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(YifyStreaming_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
