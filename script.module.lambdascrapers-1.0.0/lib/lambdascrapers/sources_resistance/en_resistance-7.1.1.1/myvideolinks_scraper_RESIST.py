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
from salts_lib.trans_utils import i18n
from salts_lib.constants import VIDEO_TYPES

BASE_URL = 'http://movies.myvideolinks.xyz'

class MyVidLinks_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'MyVideoLinks.eu'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s (%s Views)' % (item['quality'], item['host'], item['views'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)

            views = None
            pattern = '<span[^>]+>(\d+)\s+Views'
            match = re.search(pattern, html)
            if match:
                views = int(match.group(1))

            if video.video_type == VIDEO_TYPES.MOVIE:
                return self.__get_movie_links(video, views, html)
            else:
                return self.__get_episode_links(video, views, html)
        return hosters

    def __get_movie_links(self, video, views, html):
        pattern = '<h1>[^>]*>([^<]+)'
        match = re.search(pattern, html)
        q_str = ''
        if match:
            q_str = match.group(1)
        
        match = re.search('<p>Size:(.*)', html, re.DOTALL)
        if match:
            fragment = match.group(1)
        else:
            fragment = html

        return self.__get_links(video, views, fragment, q_str)

    def __get_episode_links(self, video, views, html):
        pattern = '<h4>(.*?)</h4>(.*?)</ul>'
        hosters = []
        for match in re.finditer(pattern, html, re.DOTALL):
            q_str, fragment = match.groups()
            hosters += self.__get_links(video, views, fragment, q_str)
        return hosters

    def __get_links(self, video, views, html, q_str):
        pattern = 'li>\s*<a\s+href="(http[^"]+)'
        hosters = []
        for match in re.finditer(pattern, html, re.DOTALL):
            url = match.group(1)
            hoster = {'multi-part': False, 'class': self, 'views': views, 'url': url, 'rating': None, 'quality': None, 'direct': False}
            hoster['host'] = urlparse.urlsplit(url).hostname
            hoster['quality'] = self._blog_get_quality(video, q_str, hoster['host'])
            hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return self._blog_get_url(video)

    @classmethod
    def get_settings(cls):
        settings = super(MyVidLinks_Scraper, cls).get_settings()
        settings = cls._disable_sub_check(settings)
        name = cls.get_name()
        settings.append('         <setting id="%s-filter" type="slider" range="0,180" option="int" label="     %s" default="30" visible="eq(-6,true)"/>' % (name, i18n('filter_results_days')))
        settings.append('         <setting id="%s-select" type="enum" label="     %s" lvalues="30636|30637" default="0" visible="eq(-7,true)"/>' % (name, i18n('auto_select')))
        return settings

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/?s=')
        search_url += urllib.quote_plus(title)
        html = self._http_get(search_url, cache_limit=1)
        pattern = '<h\d+>.*?<a\s+href="(?P<url>[^"]*/(?P<date>\d{4}/\d{2}/\d{2})/[^"]*)"\s+rel="bookmark"\s+title="(?P<post_title>[^"]+)'
        date_format = '%Y/%m/%d'
        return self._blog_proc_results(html, pattern, date_format, video_type, title, year)

    def _http_get(self, url, data=None, cache_limit=8):
        return super(MyVidLinks_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
