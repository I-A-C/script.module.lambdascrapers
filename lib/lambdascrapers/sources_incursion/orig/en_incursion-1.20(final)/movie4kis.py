# -*- coding: utf-8 -*-

"""
    Incursion Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import urllib
import urlparse, sys
from bs4 import BeautifulSoup
import requests

from resources.lib.modules import cache
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser2


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movie4k.is','movie4k.ws']
        self.base_link = 'http://www.movie4k.is'
        self.search_link = '/?s=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            year = url['year']
            h = {'User-Agent': client.randomagent()}
            title = cleantitle.geturl(url['title']).replace('-', '+')
            url = urlparse.urljoin(self.base_link, self.search_link % title)
            r = requests.get(url, headers=h)
            r = BeautifulSoup(r.text, 'html.parser').find('div', {'class': 'item'})
            r = r.find('a')['href']
            r = requests.get(r, headers=h)
            r = BeautifulSoup(r.content, 'html.parser')
            quality = r.find('span', {'class': 'calidad2'}).text
            url = r.find('div', {'class':'movieplay'}).find('iframe')['src']
            if not quality in ['1080p', '720p']:
                quality = 'SD'

            valid, host = source_utils.is_host_valid(url, hostDict)
            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
            return sources
        except:
            print("Unexpected error in Furk Script: check_api", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return sources

    def resolve(self, url):
        try:
            return url
        except:
            return
