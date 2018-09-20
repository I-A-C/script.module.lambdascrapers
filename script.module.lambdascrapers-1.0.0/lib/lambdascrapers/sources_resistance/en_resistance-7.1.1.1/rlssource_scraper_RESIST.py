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

BASE_URL = 'http://rlssource.net'

class RLSSource_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'RLSSource.net'

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
            
            q_str = ''
            match = re.search('class="entry-title">([^<]+)', html)
            if match:
                q_str = match.group(1)

            pattern = 'href="?([^" ]+)(?:[^>]+>){2}\s+\|'
            for match in re.finditer(pattern, html, re.DOTALL):
                url = match.group(1)
                if 'adf.ly' in url:
                    continue
                
                hoster = {'multi-part': False, 'class': self, 'views': None, 'url': url, 'rating': None, 'quality': None, 'direct': False}
                hoster['host'] = urlparse.urlsplit(url).hostname
                hoster['quality'] = self._blog_get_quality(video, q_str, hoster['host'])
                hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return self._blog_get_url(video, delim=' ')

    @classmethod
    def get_settings(cls):
        settings = super(RLSSource_Scraper, cls).get_settings()
        settings = cls._disable_sub_check(settings)
        name = cls.get_name()
        settings.append('         <setting id="%s-filter" type="slider" range="0,180" option="int" label="     Filter results older than (0=No Filter) (days)" default="30" visible="eq(-6,true)"/>' % (name))
        settings.append('         <setting id="%s-select" type="enum" label="     Automatically Select" values="Most Recent|Highest Quality" default="0" visible="eq(-7,true)"/>' % (name))
        return settings

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/?s=%s&go=Search' % (urllib.quote_plus(title)))
        html = self._http_get(search_url, cache_limit=1)
        pattern = 'href="(?P<url>[^"]+)[^>]+rel="bookmark">(?P<post_title>[^<]+).*?class="entry-date">(?P<date>\d+/\d+/\d+)'
        date_format = '%m/%d/%Y'
        return self._blog_proc_results(html, pattern, date_format, video_type, title, year)

    def _http_get(self, url, data=None, cache_limit=8):
        return super(RLSSource_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
