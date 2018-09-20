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
from salts_lib import dom_parser
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES

BASE_URL = 'http://movie.pubfilmno1.com'

class PubFilm_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'pubfilm'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        label = '[%s] %s' % (item['quality'], item['host'])
        if 'views' in item and item['views']:
            label += ' (%s views)' % item['views']
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            
            views = None
            fragment = dom_parser.parse_dom(html, 'span', {'class': 'post-views'})
            if fragment:
                fragment = fragment[0]
                views = re.sub('[^\d]', '', fragment)
                
            iframe_items = set(dom_parser.parse_dom(html, 'iframe', ret='src'))
            link_items = set(dom_parser.parse_dom(html, 'a', {'target': 'EZWebPlayer'}, ret='href'))
            items = list(iframe_items | link_items)
            for item in items:
                if item:
                    links = self.__get_links(item)
                    for link in links:
                        hoster = {'multi-part': False, 'url': link, 'class': self, 'quality': self._height_get_quality(links[link]), 'host': self._get_direct_hostname(link), 'rating': None, 'views': views, 'direct': True}
                        hosters.append(hoster)

        return hosters

    def __get_links(self, url):
        url = url.replace('&#038;', '&')
        html = self._http_get(url, cache_limit=.5)
        links = {}
        for match in re.finditer('file\s*:\s*"([^"]+)"\s*,\s*label\s*:\s*"([^"]+)p', html):
            links[match.group(1)] = match.group(2)
        
        for match in re.finditer('<source\s+src=\'([^\']+)[^>]*data-res="([^"]+)P', html):
            links[match.group(1)] = match.group(2)
        
        return links

    def get_url(self, video):
        return super(PubFilm_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        search_url = urlparse.urljoin(self.base_url, '/feeds/posts/summary?alt=json&q=%s&max-results=9999&callback=showResult')
        search_url = search_url % (urllib.quote(title))
        html = self._http_get(search_url, cache_limit=0)
        results = []
        match = re.search('showResult\((.*)\)', html)
        if match:
            js_data = match.group(1)
            if js_data:
                try:
                    js_data = json.loads(js_data)
                except ValueError:
                    log_utils.log('Invalid JSON returned: %s: %s' % (search_url, html), xbmc.LOGWARNING)
                else:
                    if 'feed' in js_data and 'entry' in js_data['feed']:
                        for entry in js_data['feed']['entry']:
                            for category in entry['category']:
                                if category['term'].upper() == 'MOVIES':
                                    break
                            else:
                                # if no movies category found, skip entry
                                continue
                            
                            for link in entry['link']:
                                if link['rel'] == 'alternate' and link['type'] == 'text/html':
                                    match = re.search('(.*?)\s*(\d{4})\s*-\s*', link['title'])
                                    if match:
                                        match_title, match_year = match.groups()
                                    else:
                                        match_title = link['title']
                                        match_year = ''
                                    
                                    if not year or not match_year or year == match_year:
                                        result = {'url': link['href'].replace(self.base_url, ''), 'title': match_title, 'year': match_year}
                                        results.append(result)
        return results

    def _http_get(self, url, cache_limit=8):
        html = super(PubFilm_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cache_limit=cache_limit)
        cookie = self._get_sucuri_cookie(html)
        if cookie:
            log_utils.log('Setting Pubfilm cookie: %s' % (cookie), xbmc.LOGDEBUG)
            html = super(PubFilm_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, cookies=cookie, cache_limit=0)
        return html
