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
import json
import xbmcaddon
import xbmc
from salts_lib import log_utils
from salts_lib.trans_utils import i18n
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://niter.co'
PHP_URL = BASE_URL + '/player/pk/pk/plugins/player_p2.php'
MAX_TRIES = 3

class Niter_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))
        self.username = xbmcaddon.Addon().getSetting('%s-username' % (self.get_name()))
        self.password = xbmcaddon.Addon().getSetting('%s-password' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'niter.tv'

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

            match = re.search('((?:pic|emb|vb)=[^<]+)', html)
            if match:
                embeds = match.group(1)
                for stream_url in embeds.split('&'):
                    if stream_url.startswith('vb='):
                        stream_url = 'http://www.vidbux.com/%s' % (stream_url[3:])
                        host = 'vidbux.com'
                        direct = False
                        quality = self._get_quality(video, host, QUALITIES.HD1080)
                    elif stream_url.startswith('pic='):
                        data = {'url': stream_url[4:]}
                        html = self._http_get(PHP_URL, data=data, auth=False, cache_limit=0)
                        try:
                            js_data = json.loads(html)
                        except ValueError:
                            log_utils.log('Invalid JSON returned: %s (%s): %s' % (PHP_URL, stream_url, html), xbmc.LOGWARNING)
                            continue
                        else:
                            host = self._get_direct_hostname(stream_url)
                            direct = True
                            for item in js_data:
                                if 'medium' in item and item['medium'] == 'video':
                                    stream_url = item['url']
                                    quality = self._width_get_quality(item['width'])
                                    break
                            else:
                                continue
                    elif stream_url.startswith('emb='):
                        stream_url = stream_url.replace('emb=', '')
                        host = urlparse.urlparse(stream_url).hostname
                        direct = False
                        quality = self._get_quality(video, host, QUALITIES.HD720)
                    else:
                        continue

                    hoster = {'multi-part': False, 'host': host, 'class': self, 'quality': quality, 'views': None, 'rating': None, 'url': stream_url, 'direct': direct}
                    hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return super(Niter_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/search?q=')
        search_url += urllib.quote(title)
        html = self._http_get(search_url, cache_limit=.25)
        results = []
        pattern = 'data-name="([^"]+).*?href="([^"]+)'
        for match in re.finditer(pattern, html, re.DOTALL):
            match_title, url = match.groups()
            result = {'title': match_title, 'year': '', 'url': url.replace(self.base_url, '')}
            results.append(result)
        return results

    @classmethod
    def get_settings(cls):
        settings = super(Niter_Scraper, cls).get_settings()
        name = cls.get_name()
        settings.append('         <setting id="%s-username" type="text" label="     %s" default="" visible="eq(-6,true)"/>' % (name, i18n('username')))
        settings.append('         <setting id="%s-password" type="text" label="     %s" option="hidden" default="" visible="eq(-7,true)"/>' % (name, i18n('password')))
        return settings

    def _http_get(self, url, data=None, auth=True, cache_limit=8):
        # return all uncached blank pages if no user or pass
        if not self.username or not self.password:
            return ''

        html = super(Niter_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
        if auth and not re.search('href="[^"]+/logout"', html):
            log_utils.log('Logging in for url (%s)' % (url), xbmc.LOGDEBUG)
            self.__login()
            html = super(Niter_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=0)

        return html

    def __login(self):
        url = urlparse.urljoin(self.base_url, '/sessions')
        data = {'username': self.username, 'password': self.password, 'remember': 1}
        html = super(Niter_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, allow_redirect=False, cache_limit=0)
        if html != self.base_url:
            raise Exception('niter.tv login failed')
