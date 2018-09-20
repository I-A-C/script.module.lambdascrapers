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
from salts_lib import dom_parser
from salts_lib.trans_utils import i18n
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://tv-release.net'
QUALITY_MAP = {'MOVIES-XVID': QUALITIES.MEDIUM, 'TV-XVID': QUALITIES.HIGH, 'TV-MP4': QUALITIES.HIGH,
               'TV-480P': QUALITIES.HIGH, 'MOVIES-480P': QUALITIES.HIGH, 'TV-720P': QUALITIES.HD720, 'MOVIES-720P': QUALITIES.HD720}

class TVReleaseNet_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'TVRelease.Net'

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
            match = re.search('>Category.*?td_col">([^<]+)', html)
            if match:
                q_str = match.group(1).upper()

            pattern = "td_cols.*?href='([^']+)"
            for match in re.finditer(pattern, html):
                url = match.group(1)
                if re.search('\.rar(\.|$)', url):
                    continue

                hoster = {'multi-part': False, 'class': self, 'views': None, 'url': url, 'rating': None, 'direct': False}
                hoster['host'] = urlparse.urlsplit(url).hostname
                hoster['quality'] = self._get_quality(video, hoster['host'], QUALITY_MAP.get(q_str, None))
                hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return self._blog_get_url(video, delim=' ')

    @classmethod
    def get_settings(cls):
        settings = super(TVReleaseNet_Scraper, cls).get_settings()
        settings = cls._disable_sub_check(settings)
        name = cls.get_name()
        settings.append('         <setting id="%s-filter" type="slider" range="0,180" option="int" label="     %s" default="30" visible="eq(-6,true)"/>' % (name, i18n('filter_results_days')))
        settings.append('         <setting id="%s-select" type="enum" label="     %s" lvalues="30636|30637" default="0" visible="eq(-7,true)"/>' % (name, i18n('auto_select')))
        return settings

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/?s=')
        search_url += urllib.quote(title)
        if video_type == VIDEO_TYPES.EPISODE:
            search_url += '&cat=TV-XviD,TV-Mp4,TV-720p,TV-480p,'
        else:
            search_url += '&cat=Movies-XviD,Movies-720p,Movies-480p'
        html = self._http_get(search_url, cache_limit=.25)
        tables = dom_parser.parse_dom(html, 'table', {'class': 'posts_table'})
        if tables:
            del tables[0]
            html = ''.join(tables)
            pattern = "<a[^>]+>(?P<quality>[^<]+).*?href='(?P<url>[^']+)'>(?P<post_title>[^<]+).*?(?P<date>[^>]+)</td></tr>"
            date_format = '%Y-%m-%d %H:%M:%S'
            return self._blog_proc_results(html, pattern, date_format, video_type, title, year)
        else:
            return []

    def _http_get(self, url, cache_limit=8):
        return super(TVReleaseNet_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
