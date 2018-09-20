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
import json
import xbmc
import time
from salts_lib import log_utils
from salts_lib import dom_parser
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import USER_AGENT
from salts_lib import kodi

BASE_URL = 'http://dizimag.co'
GIVEVIDEO_URL = '/service/givevideo'
DMG_URL1 = '/service/idmg?type=%s&a=%s&b=1%s&s=%s&e=%s&_=%s'
DMG_URL2 = '/service/vdmg?type=%s&a=%s&b=1%s&s=%s&e=%s&_=%s'
XHR = {'X-Requested-With': 'XMLHttpRequest'}

class Dizimag_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = kodi.get_setting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'Dizimag'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        label = '[%s] %s ' % (item['quality'], item['host'])
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            page_url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(page_url, cache_limit=.5)
            
            for match in re.finditer('onclick\s*=\s*"Change_Source\(\s*(\d+)\s*,\s*\'([^\']+)\'\s*\)', html):
                vid_id, host = match.groups()
                if host == 'Roosy':
                    url_type = host
                    a = 'awQa5s14d5s6s12s'
                    dmg_url = DMG_URL2
                else:
                    url = urlparse.urljoin(self.base_url, GIVEVIDEO_URL)
                    data = {'i': vid_id, 'n': host, 'p': 0}
                    html = self._http_get(url, data=data, headers=XHR, cache_limit=0)
                
                    try:
                        js_data = json.loads(html)
                    except ValueError:
                        log_utils.log('Invalid JSON returned: %s: %s' % (url, html), xbmc.LOGWARNING)
                    else:
                        url_type = js_data['p']['tur']
                        a = js_data['p']['c']
                        dmg_url = DMG_URL1

                b = vid_id
                now = int(time.time() * 1000)
                match = re.search('/([^/]+)/(.*)-izle-dizi', source_url)
                if match:
                    s, e = match.groups()
                    dmg_url = dmg_url % (url_type, a, b, s, e, now)
                    url = urlparse.urljoin(self.base_url, dmg_url)
                    html = self._http_get(url, headers=XHR, cache_limit=1)
                    match = re.search('var\s+kaynaklar\s*=\s*\[([^]]+)', html)
                    if match:
                        for match in re.finditer('file\s*:\s*"([^"]+)"\s*,\s*label\s*:\s*"(\d+)p?"', match.group(1)):
                            stream_url, height = match.groups()
                            stream_url = stream_url.decode('unicode_escape')
                            host = self._get_direct_hostname(stream_url)
                            if  host == 'gvideo':
                                quality = self._gv_get_quality(stream_url)
                            else:
                                quality = self._height_get_quality(height)
                                stream_url += '|User-Agent=%s&Referer=%s' % (USER_AGENT, page_url)

                            hoster = {'multi-part': False, 'host': host, 'class': self, 'quality': quality, 'views': None, 'rating': None, 'url': stream_url, 'direct': True}
                            hosters.append(hoster)
    
        return hosters

    def get_url(self, video):
        return super(Dizimag_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href="([^"]+/%s-sezon-%s-bolum[^"]*)"' % (video.season, video.episode)
        title_pattern = 'class="gizle".*?href="([^"]+)">([^<]+)'
        return super(Dizimag_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern)

    def search(self, video_type, title, year):
        html = self._http_get(self.base_url, cache_limit=8)
        results = []
        fragment = dom_parser.parse_dom(html, 'div', {'id': 'fil'})
        norm_title = self._normalize_title(title)
        if fragment:
            for match in re.finditer('href="([^"]+)"\s+title="([^"]+)', fragment[0]):
                url, match_title = match.groups()
                if norm_title in self._normalize_title(match_title):
                    result = {'url': url.replace(self.base_url, ''), 'title': match_title, 'year': ''}
                    results.append(result)

        return results

    def _http_get(self, url, data=None, headers=None, cache_limit=8):
        return super(Dizimag_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, headers=headers, cache_limit=cache_limit)
