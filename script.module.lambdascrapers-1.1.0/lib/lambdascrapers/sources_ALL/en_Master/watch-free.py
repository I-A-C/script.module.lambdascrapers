# -*- coding: utf-8 -*-
# - Fixed
'''
    Yoda Add-on

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


import re,urllib,urlparse,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watchfree.to','watchfree.unblockall.org', 'itswatchseries.to', 'dwatchseries.to']
        self.base_link = 'http://dwatchseries.to'
        self.search = '/search/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        pass


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            query = self.search % urllib.quote_plus(cleantitle.query(tvshowtitle))
            url = urlparse.urljoin(self.base_link, query)

            result = client.request(url)

            search_list = re.findall('<a href="(.+?\/serie\/.+?)" title="(.+?)"', result)

            for found in search_list:
                if tvshowtitle in found[1]:
                    url = found[0]
                    break

            return url

        except Exception:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            result = client.request(url)

            url = re.findall('a href="(.+?_s%s_e%s.+?)"' % (season, episode), result)[0]

            return url
            
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            result = client.request(url)

            links = re.findall('href=".+?\.html\?r=(.+?)"', result)

            for i in links:
                try:
                    url = base64.b64decode(i)
                    host = urlparse.urlparse(url).hostname

                    sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources

        except:
            return


    def resolve(self, url):
        return url
