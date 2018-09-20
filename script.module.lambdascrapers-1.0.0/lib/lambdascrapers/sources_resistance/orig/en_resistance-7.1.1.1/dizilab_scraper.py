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

BASE_URL = 'http://dizilab.com'

class Dizilab_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'Dizilab'

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
    
            for match in re.finditer('{\s*file\s*:\s*"([^"]+)', html):
                stream_url = match.group(1)
                if 'dizlab' in stream_url.lower():
                    continue
                hoster = {'multi-part': False, 'host': self._get_direct_hostname(stream_url), 'class': self, 'quality': self._gv_get_quality(stream_url), 'views': None, 'rating': None, 'url': stream_url, 'direct': True}
                hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(Dizilab_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'class="episode"\s+href="([^"]+/sezon-%s/bolum-%s)"' % (video.season, video.episode)
        title_pattern = 'class="episode-name"\s+href="([^"]+)">([^<]+)'
        return super(Dizilab_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/arsiv?limit=&tur=&orderby=&ulke=&order=&yil=&dizi_adi=')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=8)
        results = []
        for item in dom_parser.parse_dom(html, 'div', {'class': 'tv-series-single'}):
            try:
                url = re.search('href="([^"]+)', item).group(1)
            except:
                url = ''

            try:
                match_year = re.search('<span>\s*(\d{4})\s*</span>', item).group(1)
            except:
                match_year = ''
            
            try:
                match_title = dom_parser.parse_dom(item, 'a', {'class': 'title'})
                re.search('([^>]+)$', match_title[0]).group(1)
            except:
                match_title = ''
                
            if url and match_title and (not year or not match_year or year == match_year):
                result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': ''}
                results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(Dizilab_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
