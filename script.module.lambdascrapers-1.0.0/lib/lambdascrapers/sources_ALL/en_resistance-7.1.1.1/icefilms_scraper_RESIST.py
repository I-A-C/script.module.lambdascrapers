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
import urllib
import urlparse
import HTMLParser
import string
import xbmcaddon
import random
import xbmcgui
import xbmc
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

QUALITY_MAP = {'HD 720P': QUALITIES.HD720, 'DVDRIP / STANDARD DEF': QUALITIES.HIGH, 'DVD SCREENER': QUALITIES.HIGH}
BASE_URL = 'http://www.icefilms.info'
LIST_URL = BASE_URL + '/membersonly/components/com_iceplayer/video.php?h=374&w=631&vid=%s&img='
AJAX_URL = '/membersonly/components/com_iceplayer/video.phpAjaxResp.php?id=%s&s=%s&iqs=&url=&m=%s&cap= &sec=%s&t=%s&ad_url=%s'

class IceFilms_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'IceFilms'

    def resolve_link(self, link):
        url, query = link.split('?', 1)
        data = urlparse.parse_qs(query, True)
        url = urlparse.urljoin(self.base_url, url)
        url += '?s=%s&t=%s&app_id=SALTS' % (data['id'][0], data['t'][0])
        list_url = LIST_URL % (data['t'][0])
        headers = {
                   'Referer': list_url
        }
        ad_url = urllib.unquote(data['ad_url'][0])
        del data['ad_url']
        html = self._http_get(url, data=data, headers=headers, cache_limit=0)
        match = re.search('url=(.*)', html)
        if match:
            self.__show_ice_ad(ad_url, list_url)
            url = urllib.unquote_plus(match.group(1))
            return url

    def format_source_label(self, item):
        label = '[%s] %s%s' % (item['quality'], item['label'], item['host'])
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        sources = []
        if source_url:
            try:
                url = urlparse.urljoin(self.base_url, source_url)
                html = self._http_get(url, cache_limit=.5)

                pattern = '<iframe id="videoframe" src="([^"]+)'
                match = re.search(pattern, html)
                frame_url = match.group(1)
                url = urlparse.urljoin(self.base_url, frame_url)
                html = self._http_get(url, cache_limit=.1)

                match = re.search('lastChild\.value="([^"]+)"(?:\s*\+\s*"([^"]+))?', html)
                secret = ''.join(match.groups(''))

                match = re.search('"&t=([^"]+)', html)
                t = match.group(1)
                
                match = re.search('(?:\s+|,)s\s*=(\d+)', html)
                s_start = int(match.group(1))
                
                match = re.search('(?:\s+|,)m\s*=(\d+)', html)
                m_start = int(match.group(1))
                
                match = re.search('<iframe[^>]*src="([^"]+)', html)
                if match:
                    ad_url = urllib.quote(match.group(1))
                else:
                    ad_url = ''

                pattern = '<div class=ripdiv>(.*?)</div>'
                for container in re.finditer(pattern, html):
                    fragment = container.group(0)
                    match = re.match('<div class=ripdiv><b>(.*?)</b>', fragment)
                    if match:
                        quality = QUALITY_MAP.get(match.group(1).upper(), QUALITIES.HIGH)
                    else:
                        quality = None

                    pattern = 'onclick=\'go\((\d+)\)\'>([^<]+)(<span.*?)</a>'
                    for match in re.finditer(pattern, fragment):
                        link_id, label, host_fragment = match.groups()
                        source = {'multi-part': False, 'quality': quality, 'class': self, 'label': label, 'rating': None, 'views': None, 'direct': False}
                        host = re.sub('(<[^>]+>|</span>)', '', host_fragment)
                        source['host'] = host.lower()
                        s = s_start + random.randint(3, 1000)
                        m = m_start + random.randint(21, 1000)
                        url = AJAX_URL % (link_id, s, m, secret, t, ad_url)
                        source['url'] = url
                        sources.append(source)
            except Exception as e:
                log_utils.log('Failure (%s) during icefilms get sources: |%s|' % (str(e), video))
        return sources

    def get_url(self, video):
        return super(IceFilms_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        if video_type == VIDEO_TYPES.MOVIE:
            url = urlparse.urljoin(self.base_url, '/movies/a-z/')
        else:
            url = urlparse.urljoin(self.base_url, '/tv/a-z/')

        if title.upper().startswith('THE '):
            first_letter = title[4:5]
        elif title.upper().startswith('A '):
            first_letter = title[2:3]
        elif title[:1] in string.digits:
            first_letter = '1'
        else:
            first_letter = title[:1]
        url = url + first_letter.upper()

        html = self._http_get(url, cache_limit=.25)
        h = HTMLParser.HTMLParser()
        html = unicode(html, 'windows-1252')
        html = h.unescape(html)
        norm_title = self._normalize_title(title)
        pattern = 'class=star.*?href=([^>]+)>(.*?)(?:\s*\((\d+)\))?</a>'
        results = []
        for match in re.finditer(pattern, html, re.DOTALL):
            url, match_title, match_year = match.groups('')
            if norm_title in self._normalize_title(match_title) and (not year or not match_year or year == match_year):
                result = {'url': url, 'title': match_title, 'year': match_year}
                results.append(result)
        return results

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href=(/ip\.php[^>]+)>%sx0?%s\s+' % (video.season, video.episode)
        title_pattern = 'class=star>\s*<a href=([^>]+)>(?:\d+x\d+\s+)+([^<]+)'
        return super(IceFilms_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern)

    def _http_get(self, url, data=None, headers=None, cache_limit=8):
        return super(IceFilms_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, headers=headers, cache_limit=cache_limit)

    def __show_ice_ad(self, ad_url, ice_referer):
        if not ad_url: return
        try:
            wdlg = xbmcgui.WindowDialog()
            if not ad_url.startswith('http:'): ad_url = 'http:' + ad_url
            log_utils.log('Getting ad page: %s' % (ad_url), xbmc.LOGDEBUG)
            headers = {'Referer': ice_referer}
            html = self._http_get(ad_url, headers=headers, cache_limit=0)
            headers = {'Referer': ad_url}
            for match in re.finditer("<img\s+src='([^']+)'\s+width='(\d+)'\s+height='(\d+)'", html):
                img_url, width, height = match.groups()
                img_url = img_url.replace('&amp;', '&')
                width = int(width)
                height = int(height)
                log_utils.log('Image in page: |%s| - (%dx%d)' % (img_url, width, height), xbmc.LOGDEBUG)
                if width > 0 and height > 0:
                    left = (1280 - width) / 2
                    img = xbmcgui.ControlImage(left, 0, width, height, img_url)
                    wdlg.addControl(img)
                else:
                    _html = self._http_get(img_url, headers=headers, cache_limit=0)

            wdlg.show()
            dialog = xbmcgui.Dialog()
            dialog.ok('Stream All The Sources', 'Continue to Video')
            match = re.search("href='([^']+)", html)
            if match and random.randint(0, 100) < 5:
                log_utils.log('Link Clicked: %s' % (match.group(1)), xbmc.LOGDEBUG)
                html = self._http_get(match.group(1), cache_limit=0)
                match = re.search("location=decode\('([^']+)", html)
                if match:
                    _html = self._http_get(match.group(1), cache_limit=0)
        finally:
            wdlg.close()
