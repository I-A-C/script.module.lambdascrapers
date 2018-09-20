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
import xbmc
import urllib
import urlparse
import re
import xbmcaddon
import time
import json
from salts_lib import log_utils
from salts_lib.trans_utils import i18n
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://www.flixanity.tv'

class Flixanity_Scraper(scraper.Scraper):
    base_url = BASE_URL
    __token = None
    __t = None

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))
        self.username = xbmcaddon.Addon().getSetting('%s-username' % (self.get_name()))
        self.password = xbmcaddon.Addon().getSetting('%s-password' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'Flixanity'

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
            pattern = '<IFRAME\s+SRC="([^"]+)'
            for match in re.finditer(pattern, html, re.DOTALL | re.I):
                url = match.group(1)
                host = self._get_direct_hostname(url)
                if host == 'gvideo':
                    direct = True
                    quality = self._gv_get_quality(url)
                else:
                    direct = False
                    host = urlparse.urlparse(url).hostname
                    quality = self._get_quality(video, host, QUALITIES.HD720)

                source = {'multi-part': False, 'url': url, 'host': host, 'class': self, 'quality': quality, 'views': None, 'rating': None, 'direct': direct}
                sources.append(source)

        return sources

    def get_url(self, video):
        return super(Flixanity_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        self.__get_tokens()
        results = []
        search_url = urlparse.urljoin(self.base_url, '/ajax/search.php?q=')
        search_url += urllib.quote_plus(title)
        timestamp = int(time.time() * 1000)
        query = {'q': title, 'limit': '100', 'timestamp': timestamp, 'verifiedCheck': self.__token}
        html = self._http_get(search_url, data=query, cache_limit=.25)
        if video_type in [VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE]:
            media_type = 'TV SHOW'
        else:
            media_type = 'MOVIE'

        if html:
            try:
                js_data = json.loads(html)
            except ValueError:
                log_utils.log('No JSON returned: %s: %s' % (search_url, html), xbmc.LOGWARNING)
            else:
                for item in js_data:
                    if item['meta'].upper().startswith(media_type):
                        result = {'title': item['title'], 'url': item['permalink'].replace(self.base_url, ''), 'year': ''}
                        results.append(result)

        return results

    def _get_episode_url(self, show_url, video):
        season_url = show_url + '/season/%s' % (video.season)
        episode_pattern = 'href="([^"]+/season/%s/episode/%s/?)"' % (video.season, video.episode)
        title_pattern = 'href="([^"]+/season/%s/episode/%s/?)"\s+title="([^"]+)'
        return super(Flixanity_Scraper, self)._default_get_episode_url(season_url, video, episode_pattern, title_pattern)

    @classmethod
    def get_settings(cls):
        settings = super(Flixanity_Scraper, cls).get_settings()
        name = cls.get_name()
        settings.append('         <setting id="%s-username" type="text" label="     %s" default="" visible="eq(-6,true)"/>' % (name, i18n('username')))
        settings.append('         <setting id="%s-password" type="text" label="     %s" option="hidden" default="" visible="eq(-7,true)"/>' % (name, i18n('password')))
        return settings

    def _http_get(self, url, data=None, cache_limit=8):
        # return all uncached blank pages if no user or pass
        if not self.username or not self.password:
            return ''

        html = super(Flixanity_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
        if '<span>Log In</span>' in html:
            log_utils.log('Logging in for url (%s)' % (url), xbmc.LOGDEBUG)
            self.__login()
            html = super(Flixanity_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=0)

        return html

    def __get_tokens(self):
        if self.__token is None or self.__t is None:
            html = super(Flixanity_Scraper, self)._cached_http_get(self.base_url, self.base_url, self.timeout, cache_limit=0)
            match = re.search("var\s+tok\s*=\s*'([^']+)", html)
            if match:
                self.__token = match.group(1)
            else:
                log_utils.log('Unable to locate Flixanity token', xbmc.LOGWARNING)
    
            match = re.search('<input type="hidden" name="t" value="([^"]+)', html)
            if match:
                self.__t = match.group(1)
            else:
                log_utils.log('Unable to locate Flixanity t value', xbmc.LOGWARNING)

    def __login(self):
        url = urlparse.urljoin(self.base_url, '/ajax/login.php')
        self.__get_tokens()
        data = {'username': self.username, 'password': self.password, 'action': 'login', 'token': self.__token, 't': self.__t}
        html = super(Flixanity_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=0)
        if html != '0':
            raise Exception('flixanity login failed')
