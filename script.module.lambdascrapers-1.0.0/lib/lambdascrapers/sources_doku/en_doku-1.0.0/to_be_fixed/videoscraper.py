# -*- coding: utf-8 -*-

"""
    Covenant Add-on

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

import json, urllib, urlparse

from resources.lib.modules import client
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['localhost']
        self.base_link = 'http://127.0.0.1:16735'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            return urllib.urlencode({'imdb': imdb, 'title': title, 'year': year})
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            return urllib.urlencode({'imdb': imdb, 'title': tvshowtitle, 'year': year})
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            return urllib.urlencode({'imdb': imdb, 'title': title, 'year': data['year'], 'season': season, 'episode': episode})
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            url = urlparse.urljoin(self.base_link, '/sources?%s' % urllib.urlencode(data))
            r = client.request(url)
            if not r: raise Exception()
            result = json.loads(r)
            try:
                gvideos = [i['url'] for i in result if i['source'] == 'GVIDEO']
                for url in gvideos:
                    gtag = directstream.googletag(url)[0]
                    sources.append({'source': 'gvideo', 'quality': gtag['quality'], 'language': 'en', 'url': gtag['url'], 'direct': True, 'debridonly': False})
            except:
                pass

            try:
                oloads = [i['url'] for i in result if i['source'] == 'CDN']
                for url in oloads:
                    sources.append({'source': 'CDN', 'quality': 'HD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
            except:
                pass

            return sources
        except:
            return sources

    def resolve(self, url):
        if 'googlevideo' in url:
            return directstream.googlepass(url)

        return url
