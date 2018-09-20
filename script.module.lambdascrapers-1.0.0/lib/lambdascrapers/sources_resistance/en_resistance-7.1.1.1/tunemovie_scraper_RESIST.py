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
import base64
from salts_lib import dom_parser
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES
from salts_lib.constants import Q_ORDER

BASE_URL = 'http://tunemovie.is'
GK_KEY = base64.b64decode('Q05WTmhPSjlXM1BmeFd0UEtiOGg=')

class TuneMovie_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'tunemovie'

    def resolve_link(self, link):
        if self.base_url in link:
            html = self._http_get(link, cache_limit=.5)
            match = re.search('<iframe[^>]*src="([^"]+)', html)
            if match:
                link = match.group(1)

        return link

    def format_source_label(self, item):
        label = '[%s] %s' % (item['quality'], item['host'])
        if 'views' in item and item['views']:
            label += ' (%s views)' % item['views']
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            
            views = None
            match = re.search('<li>\s*Views\s*:\s*(.*?)</li>', html)
            if match:
                views = re.sub('[^0-9]', '', match.group(1))
                
            hosts = dom_parser.parse_dom(html, 'p', {'class': 'server_servername'})
            links = dom_parser.parse_dom(html, 'p', {'class': 'server_play'})
            
            for item in zip(hosts, links):
                host, link_text = item
                host = host.lower().replace('server', '').strip()
                match = re.search('href="([^"]+)', link_text)
                if match:
                    link = match.group(1)
                    if 'google' in host:
                        sources = self.__get_google_links(link)
                        for source in sources:
                            hoster = {'multi-part': False, 'url': source, 'class': self, 'quality': self._gv_get_quality(source), 'host': self._get_direct_hostname(source), 'rating': None, 'views': views, 'direct': True}
                            hosters.append(hoster)
                    else:
                            hoster = {'multi-part': False, 'url': link, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'host': host, 'rating': None, 'views': views, 'direct': False}
                            hosters.append(hoster)

        return hosters

    def __get_google_links(self, link):
        sources = {}
        html = self._http_get(link, cache_limit=.5)
        match = re.search('base64\.decode\("([^"]+)', html, re.I)
        if match:
            match = re.search('proxy\.link=tunemovie\*([^&]+)', base64.b64decode(match.group(1)))
            if match:
                picasa_url = self._gk_decrypt(GK_KEY, match.group(1))
                sources = self._parse_google(picasa_url)
        return sources

    def get_url(self, video):
        return super(TuneMovie_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/search-movies/%s.html')
        search_url = search_url % (urllib.quote_plus(title))
        html = self._http_get(search_url, cache_limit=0)
        results = []
        for thumb in dom_parser.parse_dom(html, 'div', {'class': 'thumb'}):
            match_year = dom_parser.parse_dom(thumb, 'div', {'class': '[^"]*status-year[^"]*'})
            if match_year:
                match_year = match_year[0]
            else:
                match_year = ''
            
            match = re.search('title="([^"]+)"\s+href="([^"]+)"', thumb)
            if match:
                match_title, url = match.groups()
                if not year or not match_year or year == match_year:
                    result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': match_year}
                    results.append(result)
        return results

    def _http_get(self, url, cache_limit=8):
        return super(TuneMovie_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
