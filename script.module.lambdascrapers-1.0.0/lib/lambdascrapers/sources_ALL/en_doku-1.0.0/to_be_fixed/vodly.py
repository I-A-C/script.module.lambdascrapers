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

import re, urlparse, urllib, base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import dom_parser2


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vodly.us', 'vodly.unblocked.pro']
        self.base_link = 'http://vodly.us'
        self.search_link = '/search?s=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            items = []
            clean_title = cleantitle.geturl(title) +'-'+ year
            search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
            r = cache.get(client.request, 1, search_url)
            r = client.parseDOM(r, 'div', {'class': 'col-sm-12'})
            r = client.parseDOM(r, 'div', {'class': 'col-sm-2.+?'})
            r1 = client.parseDOM(r, 'h3')
            r1 = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0])for i in r1]
            y = [re.findall('</i>\s*(\d{4})</span>', i) for i in r]

            items += [(r1[i], y[i]) for i in range(len(y))]

            r = [(i[0][0], i[1][0], i[0][1]) for i in items if
                 (cleantitle.get(i[0][1]) == cleantitle.get(title) and i[1][0] == year)]
            url = r[0][0]

            return url
        except Exception:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            url = urlparse.urljoin(self.base_link,url)
            r = cache.get(client.request, 1, url)
            try:
                v = client.parseDOM(r, 'iframe', ret='data-src')[0]

                url = v.split('=')[1]
                try:
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': 'en',
                        'url': url.replace('\/', '/'),
                        'direct': False,
                        'debridonly': False
                    })
                except:
                    pass
            except:
                pass
            r = client.parseDOM(r, 'tbody')
            r = client.parseDOM(r, 'tr')
            r = [(re.findall('<td>(.+?)</td>', i)[0], client.parseDOM(i, 'a', ret='href')[0]) for i in r]

            if r:
                for i in r:
                    try:
                        host = i[0]
                        url = urlparse.urljoin(self.base_link, i[1])
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        if 'other'in host: continue
                        sources.append({
                            'source': host,
                            'quality': 'SD',
                            'language': 'en',
                            'url': url.replace('\/', '/'),
                            'direct': False,
                            'debridonly': False
                        })
                    except:
                        pass
            return sources
        except Exception:
            return

    def resolve(self, url):
        if self.base_link in url:
            url = client.request(url)
            url = client.parseDOM(url, 'div', attrs={'class': 'wrap'})
            url = client.parseDOM(url, 'a', ret='href')[0]
        return url