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

BASE_URL = 'http://watchseries.ag'

class WS_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'WatchSeries'

    def resolve_link(self, link):
        url = urlparse.urljoin(self.base_url, link)
        html = self._http_get(url, cache_limit=0)
        match = re.search('class\s*=\s*"myButton"\s+href\s*=\s*"(.*?)"', html)
        if match:
            return match.group(1)

    def format_source_label(self, item):
        return '[%s] %s (%s/100)' % (item['quality'], item['host'], item['rating'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        sources = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            try:
                match = re.search('>English Audio.*?</tbody>\s*</table>', html, re.DOTALL)
                if match:
                    fragment = match.group(0)
                    pattern = 'href\s*=\s*"([^"]*)"\s+class\s*=\s*"buttonlink"\s+title\s*=([^\s]*).*?<span class="percent"[^>]+>\s+(\d+)%\s+</span>'
                    for match in re.finditer(pattern, fragment, re.DOTALL):
                        url, host, rating = match.groups()
                        source = {'multi-part': False, 'url': url, 'host': host, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'class': self, 'views': None, 'direct': False}
                        source['rating'] = int(rating)
                        sources.append(source)
            except Exception as e:
                log_utils.log('Failure During %s get sources: %s' % (self.get_name(), str(e)))

        return sources

    def get_url(self, video):
        return super(WS_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/search/')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=.25)

        pattern = '<a title="watch[^"]+"\s+href="(.*?)"><b>(.*?)</b>'
        results = []
        for match in re.finditer(pattern, html):
            url, title_year = match.groups()
            match = re.search('(.*?)\s+\((\d{4})\)', title_year)
            if match:
                title = match.group(1)
                res_year = match.group(2)
            else:
                title = title_year
                res_year = ''
            if not year or year == res_year:
                result = {'url': url, 'title': title, 'year': res_year}
                results.append(result)
        return results

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href="(/episode/[^"]*_s%s_e%s\..*?)"' % (video.season, video.episode)
        title_pattern = 'href="(/episode[^"]+).*?(?:&nbsp;)+([^<]+)'
        airdate_pattern = 'href="(/episode/[^"]+)(?:[^>]+>){4}\s+{p_day}/{p_month}/{year}'
        return super(WS_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern, airdate_pattern)

    def _http_get(self, url, cache_limit=8):
        return super(WS_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)

    @classmethod
    def get_settings(cls):
        settings = super(WS_Scraper, cls).get_settings()
        settings = cls._disable_sub_check(settings)
        return settings
