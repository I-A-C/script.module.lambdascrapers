# NEEDS FIXING

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


import re,json,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watch32hd.co']
        self.base_link = 'https://watch32hd.co'
        self.search_link = '/watch?v=%s_%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title'] ; year = data['year']

            h = {'User-Agent': client.randomagent()}

            v = '%s_%s' % (cleantitle.geturl(title).replace('-', '_'), year)

            url = '/watch?v=%s' % v
            url = urlparse.urljoin(self.base_link, url)

            #c = client.request(url, headers=h, output='cookie')
            #c = client.request(urlparse.urljoin(self.base_link, '/av'), cookie=c, output='cookie', headers=h, referer=url)
            #c = client.request(url, cookie=c, headers=h, referer=url, output='cookie')

            post = urllib.urlencode({'v': v})
            u = urlparse.urljoin(self.base_link, '/video_info/iframe')

            #r = client.request(u, post=post, cookie=c, headers=h, XHR=True, referer=url)
            r = client.request(u, post=post, headers=h, XHR=True, referer=url)
            r = json.loads(r).values()
            r = [urllib.unquote(i.split('url=')[-1])  for i in r]

            for i in r:
                try: sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                except: pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return directstream.googlepass(url)


