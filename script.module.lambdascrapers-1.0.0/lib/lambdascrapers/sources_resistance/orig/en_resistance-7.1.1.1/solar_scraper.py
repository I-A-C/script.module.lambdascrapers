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
import xbmcaddon
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

QUALITY_MAP = {'HD': QUALITIES.HIGH, 'DVD': QUALITIES.HIGH, 'TV': QUALITIES.HIGH, 'LQ DVD': QUALITIES.MEDIUM, 'CAM': QUALITIES.LOW}
BASE_URL = 'https://www.solarmovie.is'

class Solar_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'SolarMovie'

    def resolve_link(self, link):
        url = urlparse.urljoin(self.base_url, link)
        html = self._http_get(url, cache_limit=.5)
        match = re.search('iframe[^>]+src="([^"]+)', html, re.I)
        if match:
            return match.group(1)

    def format_source_label(self, item):
        label = '[%s] %s' % (item['quality'], item['host'])
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)

            pattern = '<tr\s+id="link_(.*?)</tr>'
            for match in re.finditer(pattern, html, re.DOTALL):
                link = match.group(1)
                link_pattern = 'href="([^"]+)">\s*([^<]+).*?class="text">\s*([^<%]+).*?class="qualityCell[^>]*>\s*([^<]+)'
                link_match = re.search(link_pattern, link, re.DOTALL)
                if link_match:
                    url, host, rating, quality = link_match.groups()
                    host = host.strip()
                    quality = quality.upper().strip()
                    if rating == 'n/a': rating = None
                    url = url.replace('/show/', '/play/')
                    quality = QUALITY_MAP.get(quality, QUALITIES.MEDIUM)

                    hoster = {'multi-part': False, 'url': url, 'host': host, 'class': self, 'quality': self._get_quality(video, host, quality), 'views': None, 'rating': rating, 'direct': False}
                    hosters.append(hoster)

        return hosters

    def get_url(self, video):
        return super(Solar_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        if video_type == VIDEO_TYPES.MOVIE:
            is_series = 1
        else:
            is_series = 2
        search_url = urlparse.urljoin(self.base_url, '/advanced-search/?q[title]=%s&q[is_series]=%s&q[year_from]=%s&q[year_to]=%s')
        search_url = search_url % (urllib.quote_plus(title), is_series, year, year)

        results = []
        html = self. _http_get(search_url, cache_limit=.25)
        if not re.search('Nothing was found', html):
            for match in re.finditer('class="name">\s*<a\s+title="([^"]+)\s+\((\d{4})\)"\s+href="([^"]+)', html):
                title, year, url = match.groups('')
                if re.search('/season-\d+/episode-\d+', url): continue  # exclude episodes

                result = {'url': url, 'title': title, 'year': year}
                results.append(result)
        return results

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href="([^"]+/season-%s/episode-%s/)' % (video.season, video.episode)
        title_pattern = 'href="([^"]+/season-\d+/episode-\d+/)"\s+title="([^"]+)'
        airdate_pattern = '<em>{month_name}\s+{day},\s+{year}</em>\s*<span\s+class="epnomber">\s*<a\s+href="([^"]+)'
        return super(Solar_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern, title_pattern, airdate_pattern)

    def _http_get(self, url, cache_limit=8):
        return super(Solar_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
