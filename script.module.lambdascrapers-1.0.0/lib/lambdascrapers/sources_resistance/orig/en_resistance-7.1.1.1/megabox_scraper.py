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
import json
import base64
import time
import hashlib
import random
import sys
from salts_lib import pyaes
from salts_lib import log_utils
from salts_lib import kodi
from salts_lib.constants import VIDEO_TYPES

BASE_URL = 'http://www.megaboxhd.com'
SEARCH_URL = '/megaboxhd/android_api_100/index.php?select=search&q=%s&page=1&total=0&total=0'
CONTENT_URL = '/megaboxhd/android_api_100/index.php?select=detail&id=%s'
SOURCE_URL = '/megaboxhd/android_api_100/index.php?select=stream&id=%s&cataid=%s'
CONFIG_URL = '/megaboxhd/android_api_100/index.php?select=config'
EXTRA_URL = ('&os=android&version=1.0.0&versioncode=100&extra_1=26EB5D5D9DC010629E21A8A6076D86CF&'
             'deviceid=%s&extra_3=6de97ad519993642d91de9b577f75b36&extra_4=%s'
             '&extra_5=%s&token=%s&time=%s&devicename=Google-Nexus-%s-%s')

RESULT_URL = '/video_type=%s&catalog_id=%s'
EPISODE_URL = RESULT_URL + '&season=%s&episode=%s'
ANDROID_LEVELS = {'22': '5.1', '21': '5.0', '19': '4.4.4', '18': '4.3.0', '17': '4.2.0', '16': '4.1.0', '15': '4.0.4', '14': '4.0.2', '13': '3.2.0'}
COUNTRIES = ['US', 'GB', 'CA', 'DK', 'MX', 'ES', 'JP', 'CN', 'DE', 'GR']
DATA_KEY = base64.b64decode('MzkzNmI5MGU5N2RjNTIxYw==')
FILM_KEY = base64.b64decode('OTBlOTdkYzUyMWNmMDIwZQ==')
MB_USER_AGENT = "Apache-HttpClient/UNAVAILABLE (java 1.4)"
HEADERS = {
           'User-Agent': MB_USER_AGENT
        }

class Megabox_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = kodi.get_setting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'MegaboxHD'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        if 'resolution' in item:
            return '[%s] (%s) %s' % (item['quality'], item['resolution'], item['host'])
        else:
            return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        sources = []
        if source_url:
            params = urlparse.parse_qs(source_url)
            show_url = CONTENT_URL % (params['catalog_id'][0])
            url = urlparse.urljoin(self.base_url, show_url)
            html = self._http_get(url, cache_limit=.5)
            try:
                js_data = json.loads(html)
                if video.video_type == VIDEO_TYPES.EPISODE:
                    js_data = self.__get_episode_json(params, js_data)
            except ValueError:
                log_utils.log('Invalid JSON returned for: %s' % (url), xbmc.LOGWARNING)
            else:
                for film in js_data['listvideos']:
                    source_url = SOURCE_URL % (film['film_id'], params['catalog_id'][0])
                    url = urlparse.urljoin(self.base_url, source_url)
                    time.sleep(1.5)
                    html = self._http_get(url, cache_limit=.5)
                    try:
                        film_js = json.loads(html)
                    except ValueError:
                        log_utils.log('Invalid JSON returned for: %s' % (url), xbmc.LOGWARNING)
                    else:
                        for film in film_js['videos']:
                            film_link = self.__decrypt(FILM_KEY, base64.b64decode(film['film_link']))
                            for match in re.finditer('(http.*?(?:#(\d+)#)?)(?=http|$)', film_link):
                                link, height = match.groups()
                                source = {'multi-part': False, 'url': link, 'host': self._get_direct_hostname(link), 'class': self, 'quality': self._gv_get_quality(link), 'views': None, 'rating': None, 'direct': True}
                                if height is not None: source['resolution'] = '%sp' % (height)
                                sources.append(source)

        return sources

    def __get_episode_json(self, params, js_data):
            new_data = {'listvideos': []}
            for episode in js_data['listvideos']:
                if ' S%02dE%02d ' % (int(params['season'][0]), int(params['episode'][0])) in episode['film_name']:
                    new_data['listvideos'].append(episode)
            return new_data

    def get_url(self, video):
        return super(Megabox_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        results = []
        search_url = urlparse.urljoin(self.base_url, SEARCH_URL % (urllib.quote_plus(title)))
        html = self._http_get(search_url, cache_limit=.25)
        try:
            js_data = json.loads(html)
        except ValueError:
            log_utils.log('Invalid JSON returned for: %s' % (search_url), xbmc.LOGWARNING)
        else:
            for item in js_data['categories']:
                match = re.search('(.*?)\s+\((\d{4}).?\d{0,4}\s*\)', item['catalog_name'])
                if match:
                    match_title, match_year = match.groups()
                else:
                    match_title = item['catalog_name']
                    match_year = ''
                
                if not year or not match_year or year == match_year:
                    result_url = RESULT_URL % (video_type, item['catalog_id'])
                    result = {'title': match_title, 'url': result_url, 'year': match_year}
                    results.append(result)
        return results

    def _get_episode_url(self, show_url, video):
        params = urlparse.parse_qs(show_url)
        source_url = CONTENT_URL % (params['catalog_id'][0])
        url = urlparse.urljoin(self.base_url, source_url)
        html = self._http_get(url, cache_limit=.5)
        try:
            js_data = json.loads(html)
        except ValueError:
            log_utils.log('Invalid JSON returned for: %s' % (url), xbmc.LOGWARNING)
        else:
            force_title = self._force_title(video)
            if not force_title:
                for episode in js_data['listvideos']:
                    if ' S%02dE%02d ' % (int(video.season), int(video.episode)) in episode['film_name']:
                        return EPISODE_URL % (video.video_type, params['catalog_id'][0], video.season, video.episode)
            
            if (force_title or kodi.get_setting('title-fallback') == 'true') and video.ep_title:
                norm_title = self._normalize_title(video.ep_title)
                for episode in js_data['listvideos']:
                    match = re.search('-\s*S(\d+)E(\d+)\s*-\s*(.*)', episode['film_name'])
                    if match:
                        season, episode, title = match.groups()
                        if title and norm_title == self._normalize_title(title):
                            return EPISODE_URL % (video.video_type, params['catalog_id'][0], int(season), int(episode))

    @classmethod
    def get_settings(cls):
        settings = super(Megabox_Scraper, cls).get_settings()
        name = cls.get_name()
        settings.append('         <setting id="%s-last-config" type="number" default="0" visible="false"/>' % (name))
        return settings

    def _http_get(self, url, data=None, cache_limit=8):
        self.__check_config()
        url += self.__get_extra()
        result = super(Megabox_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, headers=HEADERS, cache_limit=cache_limit)
        result = result.strip()
        if result:
            return self.__decrypt(DATA_KEY, base64.b64decode(result))
        else:
            return ''
                    
    def __check_config(self):
        now = time.time()
        last_config_call = now - int(kodi.get_setting('%s-last-config' % (self.get_name())))
        if last_config_call > 8 * 60 * 60:
            url = urlparse.urljoin(self.base_url, CONFIG_URL)
            url += self.__get_extra()
            _html = super(Megabox_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, headers=HEADERS, cache_limit=8)
            kodi.set_setting('%s-last-config' % (self.get_name()), str(int(now)))
    
    def __get_extra(self):
        now = str(int(time.time()))
        build = random.choice(ANDROID_LEVELS.keys())
        device_id = hashlib.md5(str(random.randint(0, sys.maxint))).hexdigest()
        country = random.choice(COUNTRIES)
        return EXTRA_URL % (device_id, country, country.lower(), hashlib.md5(now).hexdigest(), now, build, ANDROID_LEVELS[build])
    
    def __decrypt(self, key, cipher_text):
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationECB(key))
        plain_text = decrypter.feed(cipher_text)
        plain_text += decrypter.feed()
        return plain_text
