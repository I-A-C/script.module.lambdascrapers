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
import xbmcaddon
import json
import xbmc
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES
from salts_lib.constants import Q_ORDER

Q_LIST = [item[0] for item in sorted(Q_ORDER.items(), key=lambda x:x[1])]


BASE_URL = 'http://www.alluc.com'
SEARCH_URL = '/api/search/%s/?apikey=%s&query=%s+lang%%3Aen&count=100&from=0&getmeta=0'
SEARCH_TYPES = ['stream', 'download']
API_KEY = '02216ecc1bf4bcc83a1ee6c72a5f0eda'
QUALITY_MAP = {
               QUALITIES.LOW: ['DVDSCR', 'CAMRIP', 'HDCAM'],
               QUALITIES.MEDIUM: [],
               QUALITIES.HIGH: ['BDRIP', 'BRRIP', 'HDRIP'],
               QUALITIES.HD720: ['720P'],
               QUALITIES.HD1080: ['1080P']}

class Alluc_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'alluc.com'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        if source_url:
            params = urlparse.parse_qs(urlparse.urlparse(source_url).query)
            if video.video_type == VIDEO_TYPES.MOVIE:
                query = urllib.quote_plus('%s %s' % (params['title'][0], params['year'][0]))
            else:
                query = urllib.quote_plus('%s S%02dE%02d' % (params['title'][0], int(params['season'][0]), int(params['episode'][0])))
            query_url = '/search?query=%s' % (query)
            hosters = self.__get_links(query_url, video)
            if not hosters and video.video_type == VIDEO_TYPES.EPISODE and params['air_date'][0]:
                query = urllib.quote_plus('%s %s' % (params['title'][0], params['air_date'][0].replace('-', '.')))
                query_url = '/search?query=%s' % (query)
                hosters = self.__get_links(query_url, video)

        return hosters

    def __get_links(self, url, video):
        hosters = []
        seen_urls = set()
        for search_type in SEARCH_TYPES:
            search_url = self.__translate_search(url, search_type)
            html = self._http_get(search_url, cache_limit=.5)
            if html:
                try:
                    js_result = json.loads(html)
                except ValueError:
                    log_utils.log('Invalid JSON returned: %s: %s' % (search_url, html), xbmc.LOGWARNING)
                else:
                    if js_result['status'] == 'success':
                        for result in js_result['result']:
                            if len(result['hosterurls']) > 1: continue
                            if result['extension'] == 'rar': continue
                            
                            stream_url = result['hosterurls'][0]['url']
                            if stream_url not in seen_urls:
                                if self.__title_check(video, result['title']):
                                    host = urlparse.urlsplit(stream_url).hostname.lower()
                                    quality = self._get_quality(video, host, self._get_title_quality(result['title']))
                                    hoster = {'multi-part': False, 'class': self, 'views': None, 'url': stream_url, 'rating': None, 'host': host, 'quality': quality, 'direct': False}
                                    hosters.append(hoster)
                                    seen_urls.add(stream_url)
        return hosters
        
    def __title_check(self, video, title):
        title = self._normalize_title(title)
        if video.video_type == VIDEO_TYPES.MOVIE:
            return self._normalize_title(video.title) in title and video.year in title
        else:
            sxe = 'S%02dE%02d' % (int(video.season), int(video.episode))
            se = '%d%02d' % (int(video.season), int(video.episode))
            air_date = video.ep_airdate.strftime('%Y%m%d')
            if sxe in title:
                show_title = title.split(sxe)[0]
            elif air_date in title:
                show_title = title.split(air_date)[0]
            elif se in title:
                show_title = title.split(se)[0]
            else:
                show_title = title
            #log_utils.log('%s - %s - %s - %s - %s' % (self._normalize_title(video.title), show_title, title, sxe, air_date), xbmc.LOGDEBUG)
            return self._normalize_title(video.title) in show_title and (sxe in title or se in title or air_date in title)
    
    def _get_title_quality(self, title):
        post_quality = QUALITIES.HIGH
        title = title.upper()
        for key in Q_LIST:
            if any(q in title for q in QUALITY_MAP[key]):
                post_quality = key

        #log_utils.log('Setting |%s| to |%s|' % (title, post_quality), xbmc.LOGDEBUG)
        return post_quality
    
    def get_url(self, video):
        url = None
        self.create_db_connection()
        result = self.db_connection.get_related_url(video.video_type, video.title, video.year, self.get_name(), video.season, video.episode)
        if result:
            url = result[0][0]
            log_utils.log('Got local related url: |%s|%s|%s|%s|%s|' % (video.video_type, video.title, video.year, self.get_name(), url))
        else:
            if video.video_type == VIDEO_TYPES.MOVIE:
                query = 'title=%s&year=%s' % (urllib.quote_plus(video.title), video.year)
            else:
                query = 'title=%s&season=%s&episode=%s&air_date=%s' % (urllib.quote_plus(video.title), video.season, video.episode, video.ep_airdate)
            url = '/search?%s' % (query)
            self.db_connection.set_related_url(video.video_type, video.title, video.year, self.get_name(), url)
        return url

    def search(self, video_type, title, year):
        return []

    def _http_get(self, url, cache_limit=8):
        return super(Alluc_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)

    def __translate_search(self, url, search_type):
        query = urlparse.parse_qs(urlparse.urlparse(url).query)
        return urlparse.urljoin(self.base_url, SEARCH_URL % (search_type, API_KEY, urllib.quote_plus(query['query'][0])))
