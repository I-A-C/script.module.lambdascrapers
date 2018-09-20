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
import time
import xbmcaddon
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

QUALITY_MAP = {'HD': QUALITIES.HIGH, 'HDTV': QUALITIES.HIGH, 'DVD': QUALITIES.HIGH, '3D': QUALITIES.HIGH, 'CAM': QUALITIES.LOW}
BASE_URL = 'https://www.iwatchonline.ag'

class IWatchOnline_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'iWatchOnline'

    def resolve_link(self, link):
        url = urlparse.urljoin(self.base_url, link)
        html = self._http_get(url, cache_limit=.5)
        match = re.search('<iframe name="frame" class="frame" src="([^"]+)', html)
        if match:
            return match.group(1)

    def format_source_label(self, item):
        label = '[%s] %s (%s/100)' % (item['quality'], item['host'], item['rating'])
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)

            match = re.search('<table[^>]+id="streamlinks">(.*?)</table>', html, re.DOTALL)
            if match:
                fragment = match.group(1)
                if video.video_type == VIDEO_TYPES.MOVIE:
                    pattern = 'href="([^"]+/play/[^"]+).*?/>\s+\.?([^\s]+)\s+.*?(?:<td>.*?</td>\s*){2}<td>(.*?)</td>\s*<td>(.*?)</td>'
                else:
                    pattern = 'href="([^"]+/play/[^"]+).*?/>\s+\.?([^\s]+)\s+.*?(<span class="linkdate">.*?)</td>\s*<td>(.*?)</td>'
                max_age = 0
                now = min_age = int(time.time())
                for match in re.finditer(pattern, fragment, re.DOTALL):
                    url, host, age, quality = match.groups()
                    age = self.__get_age(now, age)
                    quality = quality.upper()
                    if age > max_age: max_age = age
                    if age < min_age: min_age = age
                    hoster = {'multi-part': False, 'class': self, 'url': url.replace(self.base_url, ''), 'host': host.lower(), 'age': age, 'views': None, 'rating': None, 'direct': False}
                    hoster['quality'] = self._get_quality(video, host.lower(), QUALITY_MAP.get(quality, QUALITIES.HIGH))
                    hosters.append(hoster)

                unit = (max_age - min_age) / 100
                if unit > 0:
                    for hoster in hosters:
                        hoster['rating'] = (hoster['age'] - min_age) / unit
                        # print '%s, %s' % (hoster['rating'], hoster['age'])
        return hosters

    def __get_age(self, now, age_str):
        age_str = age_str.replace('<span class="linkdate">', '')
        age_str = age_str.replace('</span>', '')
        try:
            age = int(age_str)
        except ValueError:
            match = re.search('(\d+)\s+(.*)', age_str)
            if match:
                num, unit = match.groups()
                num = int(num)
                unit = unit.lower()
                if 'minute' in unit:
                    mult = 60
                elif 'hour' in unit:
                    mult = (60 * 60)
                elif 'day' in unit:
                    mult = (60 * 60 * 24)
                elif 'month' in unit:
                    mult = (60 * 60 * 24 * 30)
                elif 'year' in unit:
                    mult = (60 * 60 * 24 * 365)
                else:
                    mult = 0
            else:
                num = 0
                mult = 0
            age = now - (num * mult)
                # print '%s, %s, %s, %s' % (num, unit, mult, age)
        return age

    def get_url(self, video):
        return super(IWatchOnline_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/advance-search')
        if video_type == VIDEO_TYPES.MOVIE:
            data = {'searchin': '1'}
        else:
            data = {'searchin': '2'}
        data.update({'searchquery': title})
        search_url += '?' + urllib.urlencode(data)  # add criteria to url to make cache work
        html = self._http_get(search_url, data=data, cache_limit=.25)

        results = []
        pattern = r'href="([^"]+)">(.*?)\s+\((\d{4})\)'
        for match in re.finditer(pattern, html):
            url, title, match_year = match.groups('')
            if not year or not match_year or year == match_year:
                url = url.replace('/episode/', '/tv-shows/')  # fix wrong url returned from search results
                result = {'url': url.replace(self.base_url, ''), 'title': title, 'year': match_year}
                results.append(result)
        return results

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href="([^"]+-s%02de%02d)"' % (int(video.season), int(video.episode))
        title_pattern = 'href="([^"]+)"><i class="icon-play-circle">.*?<td>([^<]+)</td>'
        return super(IWatchOnline_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern)

    def _http_get(self, url, data=None, cache_limit=8):
        return super(IWatchOnline_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)
