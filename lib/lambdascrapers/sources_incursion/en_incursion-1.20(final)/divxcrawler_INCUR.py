# -*- coding: utf-8 -*-

'''
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
'''


import re,urllib,urlparse, traceback, requests

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser2

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['divxcrawler.tv']
        self.base_link = 'http://www.divxcrawler.tv'
        self.search_link = '/latest.htm'
        self.search_link2 = '/streaming.htm'
        self.search_link3 = '/movies.htm'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            data = url
            imdb = data['imdb']

            try:
                query = urlparse.urljoin(self.base_link, self.search_link)
                result = requests.get(query).text
                m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result, re.DOTALL)
                for i in m:
                    print(i)
                m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
                if m:
                    link = m
                else:
                    query = urlparse.urljoin(self.base_link, self.search_link2)
                    result = requests.get(query).text
                    m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result, re.DOTALL)
                    m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
                    if m:
                        link = m
                    else:
                        query = urlparse.urljoin(self.base_link, self.search_link3)
                        result = requests.get(query).text
                        m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result, re.DOTALL)
                        m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
                        if m: link = m

            except:
                traceback.print_exc()
                return

            for item in link:
                try:

                    quality, info = source_utils.get_release_quality(item[2], None)

                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', item[0])[-1]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except:
                        traceback.print_exc()
                        pass

                    info = ' | '.join(info)

                    url = item[2]
                    if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                                    'direct': True, 'debridonly': False})
                except:
                    traceback.print_exc()
                    pass

            return sources
        except:
            traceback.print_exc()
            return sources

    def resolve(self, url):
        return url


