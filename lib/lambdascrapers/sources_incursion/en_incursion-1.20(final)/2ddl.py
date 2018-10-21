# -*- coding: utf-8 -*-

'''
    Incursion Add-on
    Copyright (C) 2016 Incursion

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
'''

import requests
import re

from resources.lib.modules import cleantitle
from resources.lib.modules.source_utils import get_quality_simple

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['http://2ddl.io/']
        self.base_link = 'http://2ddl.io'
        self.search_link = '/search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        url = title.replace(" ", "+")
        return url


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = tvshowtitle
        return url


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):

        if len(season) == 1:
            season = "0" + season
        if len(episode) == 1:
            episode = "0" + episode

        searchterm = (url + "+s" + season + "e" + episode).replace(" ", "+")
        return searchterm

    def sources(self, url, hostDict, hostprDict):
        links = []
        sources = []

        response = requests.get(self.base_link + self.search_link % url)
        capture = re.findall(r'<singlelink><\/singlelink>((?s).*)<download><\/download>', response.text)

        for i in capture:
            links.append(re.findall(r'href="(.*?)"', i))

        links = [item for sublist in links for item in sublist]

        for i in links:
            for h in hostprDict:
                if h in i:
                    if not '.rar' in i:
                        quality = get_quality_simple(i)
                        video = {}
                        video['url'] = i
                        video['quality'] = quality
                        video['source'] = h
                        video['debridonly'] = True
                        video['language'] = 'en'
                        video['info'] = ''
                        video['direct'] = False
                        sources.append(video)

        return sources

    def resolve(self, url):
            return url
