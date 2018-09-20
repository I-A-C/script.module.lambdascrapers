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
from salts_lib import dom_parser
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://www.couchtuner.la'

class CouchTunerV1_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'CouchTunerV1'

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
            entry = ''
            while True:
                html = self._http_get(url, cache_limit=.5)
                entry = dom_parser.parse_dom(html, 'div', {'class': 'entry'})
                if entry:
                    entry = entry[0]
                    match = re.search('Watch it here\s*:.*?href="([^"]+)', entry, re.I)
                    if match:
                        url = match.group(1)
                    else:
                        break
                else:
                    entry = ''
                    break
    
            for tab in dom_parser.parse_dom(entry, 'div', {'class': '''[^'"]*postTabs_divs[^'"]*'''}):
                match = re.search('<iframe[^>]*src="([^"]+)', tab, re.I | re.DOTALL)
                if match:
                    link = match.group(1)
                    host = urlparse.urlparse(link).hostname
                    hoster = {'multi-part': False, 'host': host, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'views': None, 'rating': None, 'url': link, 'direct': False}
                    hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(CouchTunerV1_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href="([^"]+[sS](?:eason-)?%s-[eE](?:pisode-)?%s-[^"]+)' % (video.season, video.episode)
        title_pattern = 'href="([^"]+season-\d+-episode-\d+-[^"]+).*?8211;\s*([^<]+)'
        return super(CouchTunerV1_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern)

    def search(self, video_type, title, year):
        show_list_url = urlparse.urljoin(self.base_url, '/tv-lists/')
        html = self._http_get(show_list_url, cache_limit=8)
        results = []
        norm_title = self._normalize_title(title)
        items = dom_parser.parse_dom(html, 'li')
        for item in items:
            match = re.search('href="([^"]+)">(.*?)</a>', item)
            if match:
                url, match_title = match.groups()
                match_title = match_title.replace('<strong>', '').replace('</strong>', '')
                if norm_title in self._normalize_title(match_title):
                    result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': ''}
                    results.append(result)

        return results

    def _http_get(self, url, data=None, cache_limit=8):
        return super(CouchTunerV1_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
