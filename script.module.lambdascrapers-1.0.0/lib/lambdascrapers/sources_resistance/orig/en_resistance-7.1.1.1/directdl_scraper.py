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
import xbmc
import json
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://directdownload.tv'
SEARCH_URL = '/api?key=%s&%s&keyword=%s'
API_KEY = 'AFBF8E33A19787D1'

Q_ORDER = ['PDTV', 'DSR', 'DVDRIP', 'HDTV', '720P', 'WEBDL', 'WEBDL1080P']
Q_DICT = dict((quality, i) for i, quality in enumerate(Q_ORDER))
QUALITY_MAP = {'PDTV': QUALITIES.MEDIUM, 'DSR': QUALITIES.MEDIUM, 'DVDRIP': QUALITIES.HIGH,
               'HDTV': QUALITIES.HIGH, '720P': QUALITIES.HD720, 'WEBDL': QUALITIES.HD720, 'WEBDL1080P': QUALITIES.HD1080}

class DirectDownload_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'DirectDownload.tv'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] (%s) %s' % (item['quality'], item['dd_qual'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            if html:
                try:
                    js_result = json.loads(html)
                except ValueError:
                    log_utils.log('Invalid JSON returned: %s: %s' % (url, html), xbmc.LOGWARNING)
                else:
                    if 'error' in js_result:
                        log_utils.log('DD.tv API error: "%s" @ %s' % (js_result['error'], url), xbmc.LOGWARNING)
                        return hosters

                    query = urlparse.parse_qs(urlparse.urlparse(url).query)
                    match_quality = Q_ORDER
                    if 'quality' in query:
                        temp_quality = re.sub('\s', '', query['quality'][0])
                        match_quality = temp_quality.split(',')
    
                    sxe_str = '.S%02dE%02d.' % (int(video.season), int(video.episode))
                    airdate_str = video.ep_airdate.strftime('.%Y.%m.%d.')
                    for result in js_result:
                        if sxe_str not in result['release'] and airdate_str not in result['release']:
                            continue
                        
                        if result['quality'] in match_quality:
                            for key in result['links']:
                                url = result['links'][key][0]
                                if re.search('\.rar(\.|$)', url):
                                    continue
                                
                                hostname = urlparse.urlparse(url).hostname
                                hoster = {'multi-part': False, 'class': self, 'views': None, 'url': url, 'rating': None, 'host': hostname,
                                        'quality': QUALITY_MAP[result['quality']], 'dd_qual': result['quality'], 'direct': False}
                                hosters.append(hoster)

        return hosters

    def get_url(self, video):
        url = None
        self.create_db_connection()
        result = self.db_connection.get_related_url(video.video_type, video.title, video.year, self.get_name(), video.season, video.episode)
        if result:
            url = result[0][0]
            log_utils.log('Got local related url: |%s|%s|%s|%s|%s|' % (video.video_type, video.title, video.year, self.get_name(), url))
        else:
            date_match = False
            search_title = '%s S%02dE%02d' % (video.title, int(video.season), int(video.episode))
            results = self.search(video.video_type, search_title, '')
            if not results and video.ep_airdate is not None:
                search_title = '%s %s' % (video.title, video.ep_airdate.strftime('%Y.%m.%d'))
                results = self.search(video.video_type, search_title, '')
                date_match = True

            best_q_index = -1
            for result in results:
                if date_match and video.ep_airdate.strftime('%Y.%m.%d') not in result['title']:
                    continue
                
                if Q_DICT[result['quality']] > best_q_index:
                    best_q_index = Q_DICT[result['quality']]
                    url = result['url']
            self.db_connection.set_related_url(video.video_type, video.title, video.year, self.get_name(), url)
        return url

    @classmethod
    def get_settings(cls):
        settings = super(DirectDownload_Scraper, cls).get_settings()
        settings = cls._disable_sub_check(settings)
        return settings

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/search?query=')
        search_url += title
        html = self._http_get(search_url, cache_limit=.25)
        results = []
        if html:
            try:
                js_result = json.loads(html)
            except ValueError:
                log_utils.log('Invalid JSON returned: %s: %s' % (search_url, html), xbmc.LOGWARNING)
            else:
                if 'error' in js_result:
                    log_utils.log('DD.tv API error: "%s" @ %s' % (js_result['error'], search_url), xbmc.LOGWARNING)
                    return results
                
                for match in js_result:
                    url = search_url + '&quality=%s' % match['quality']
                    result = {'url': url.replace(self.base_url, ''), 'title': match['release'], 'quality': match['quality'], 'year': ''}
                    results.append(result)
        return results

    def _http_get(self, url, data=None, cache_limit=8):
        if 'search?query' in url:
            log_utils.log('Translating Search Url: %s' % (url), xbmc.LOGDEBUG)
            url = self.__translate_search(url)

        return super(DirectDownload_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)

    def __translate_search(self, url):
        query = urlparse.parse_qs(urlparse.urlparse(url).query)
        if 'quality' in query:
            q_list = re.sub('\s', '', query['quality'][0].upper()).split(',')
        else:
            q_list = Q_ORDER
        quality = '&'.join(['quality[]=%s' % (q) for q in q_list])
        return urlparse.urljoin(self.base_url, (SEARCH_URL % (API_KEY, quality, urllib.quote_plus(query['query'][0]))))
