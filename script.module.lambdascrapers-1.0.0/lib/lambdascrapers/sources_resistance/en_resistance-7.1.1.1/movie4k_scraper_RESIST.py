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
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://www.movie4k.to'
QUALITY_MAP = {None: None, '0': QUALITIES.LOW, '1': QUALITIES.LOW, '2': QUALITIES.MEDIUM, '3': QUALITIES.MEDIUM, '4': QUALITIES.HIGH, '5': QUALITIES.HIGH}

class Movie4K_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'Movie4K'

    def resolve_link(self, link):
        url = urlparse.urljoin(self.base_url, link)
        html = self._http_get(url, cache_limit=0)
        match = re.search('Check the mirror links on the left menu.*?(?:src|href)="([^"]+)', html, re.DOTALL)
        if match:
            return match.group(1)

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)

            pattern = r'id="tablemoviesindex2".*?href="([^"]+).*?&nbsp;([^<]+)(.*)'
            for match in re.finditer(pattern, html):
                url, host, extra = match.groups()
                if not url.startswith('/'): url = '/' + url
                r = re.search('/smileys/(\d+)\.gif', extra)
                if r:
                    smiley = r.group(1)
                else:
                    smiley = None

                hoster = {'multi-part': False, 'host': host.lower(), 'class': self, 'quality': self._get_quality(video, host, QUALITY_MAP[smiley]), 'views': None, 'rating': None, 'url': url, 'direct': False}
                hosters.append(hoster)
        return hosters

    def get_url(self, video):
        return super(Movie4K_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/movies.php?list=search&search=')
        search_url += urllib.quote_plus(title)
        cookies = {'onlylanguage': 'en', 'lang': 'en'}
        html = self._http_get(search_url, cookies=cookies, cache_limit=.25)
        results = []
        pattern = 'id="tdmovies">\s*<a\s+href="([^"]+)">([^<]+).*?id="f7">(.*?)</TD>'
        for match in re.finditer(pattern, html, re.DOTALL):
            url, title, extra = match.groups('')
            if (video_type == VIDEO_TYPES.MOVIE and '(TVshow)' in title) or (video_type == VIDEO_TYPES.TVSHOW and '(TVshow)' not in title):
                continue

            title = title.replace('(TVshow)', '')
            title = title.strip()

            r = re.search('>(\d{4})<', extra)
            if r:
                match_year = r.group(1)
            else:
                match_year = ''

            if not year or not match_year or year == match_year:
                url = url.replace(self.base_url, '')
                if not url.startswith('/'): url = '/' + url
                result = {'url': url, 'title': title, 'year': match_year}
                results.append(result)
        return results

    def _get_episode_url(self, show_url, video):
        if not self._force_title(video):
            url = urlparse.urljoin(self.base_url, show_url)
            html = self._http_get(url, cache_limit=.25)
            match = re.search('<div id="episodediv%s"(.*?)</div>' % (video.season), html, re.DOTALL)
            if match:
                fragment = match.group(1)
                pattern = 'value="([^"]+)">Episode %s<' % (video.episode)
                match = re.search(pattern, fragment)
                if match:
                    url = match.group(1)
                    url = url.replace(self.base_url, '')
                    if not url.startswith('/'): url = '/' + url
                    return url

    def _http_get(self, url, cookies=None, data=None, cache_limit=8):
        return super(Movie4K_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cookies=cookies, data=data, cache_limit=cache_limit)
