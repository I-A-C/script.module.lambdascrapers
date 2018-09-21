# -*- coding: utf-8 -*-

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


import re,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['mydownloadtube.com']
        self.base_link = 'http://www.mydownloadtube.com'
        self.search_link = '/search/search_val?language=English%20-%20UK&term='
        self.download_link = '/movies/add_download'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            if debrid.status() == False: raise Exception()

            t = cleantitle.get(title)

            query = self.search_link + urllib.quote_plus(title)
            query = urlparse.urljoin(self.base_link, query)

            r = client.request(query, XHR=True)
            r = json.loads(r)

            r = [i for i in r if 'category' in i and 'movie' in i['category'].lower()]
            r = [(i['url'], i['label']) for i in r if 'label' in i and 'url' in i]
            r = [(i[0], re.findall('(.+?) \((\d{4})', i[1])) for i in r]
            r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if len(i[1]) > 0]
            r = [i[0] for i in r if t == cleantitle.get(i[1]) and year == i[2]][0]

            url = re.findall('(?://.+?|)(/.+)', r)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            if debrid.status() == False: raise Exception()

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            r = client.parseDOM(r, 'input', {'id': 'movie_id'}, ret='value')
            if r:
                r = client.request(urlparse.urljoin(self.base_link, self.download_link), post='movie=%s' % r, referer=url)

            links = client.parseDOM(r, 'p')

            hostDict = hostprDict + hostDict

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]


            for link in links:
                try:
                    host = re.findall('Downloads-Server(.+?)(?:\'|\")\)', link)[0]
                    host = host.strip().lower().split()[-1]
                    if host == 'fichier': host = '1fichier'
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    url = client.parseDOM(link, 'a', ret='href')[0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    r = client.parseDOM(link, 'a')[0]

                    fmt = r.strip().lower().split()

                    if '1080p' in fmt: quality = '1080p'
                    elif '720p' in fmt: quality = 'HD'

                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) [M|G]B)', r)[-1]
                        div = 1 if size.endswith(' GB') else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                        info = '%.2f GB' % size
                    except:
                        info = ''

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = client.request(url, output='geturl')
            return url
        except:
            return


