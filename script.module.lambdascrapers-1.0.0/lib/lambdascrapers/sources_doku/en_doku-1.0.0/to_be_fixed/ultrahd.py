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

import re,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser2

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['ultrahdindir.com']
        self.base_link = 'http://ultrahdindir.com'
        self.post_link = '/index.php?do=search'

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

            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title'].replace(':','').lower()
            year = data['year']

            query = '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = urlparse.urljoin(self.base_link, self.post_link)

            post = 'do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=%s' % urllib.quote_plus(query)

            r = client.request(url, post=post)
            r = client.parseDOM(r, 'div', attrs={'class': 'box-out margin'})
            r = [(dom_parser2.parse_dom(i, 'div', attrs={'class':'news-title'})) for i in r if data['imdb'] in i]
            r = [(dom_parser2.parse_dom(i[0], 'a', req='href')) for i in r if i]
            r = [(i[0].attrs['href'], i[0].content) for i in r if i]

            hostDict = hostprDict + hostDict

            for item in r:
                try:
                    name = item[1]
                    y = re.findall('\((\d{4})\)', name)[0]
                    if not y == year: raise Exception()

                    s = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', name)
                    s = s[0] if s else '0'
                    data = client.request(item[0])
                    data = dom_parser2.parse_dom(data, 'div', attrs={'id': 'r-content'})
                    data = re.findall('\s*<b><a href=.+?>(.+?)</b>.+?<u><b><a href="(.+?)".+?</a></b></u>',
                                      data[0].content, re.DOTALL)
                    u = [(i[0], i[1], s) for i in data if i]

                    for name, url, size in u:
                        try:
                            if '4K' in name:
                                quality = '4K'
                            elif '1080p' in name:
                                quality = '1080p'
                            elif '720p' in name:
                                quality = '720p'
                            elif any(i in ['dvdscr', 'r5', 'r6'] for i in name):
                                quality = 'SCR'
                            elif any(i in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'telesync', 'ts']
                                     for i in name):
                                quality = 'CAM'
                            else: quality = '720p'

                            info = []
                            if '3D' in name or '.3D.' in url: info.append('3D'); quality = '1080p'
                            if any(i in ['hevc', 'h265', 'x265'] for i in name): info.append('HEVC')
                            try:
                                size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', size)[-1]
                                div = 1 if size.endswith(('Gb', 'GiB', 'GB')) else 1024
                                size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                                size = '%.2f GB' % size
                                info.append(size)
                            except:
                                pass

                            info = ' | '.join(info)

                            url = client.replaceHTMLCodes(url)
                            url = url.encode('utf-8')
                            if any(x in url for x in ['.rar', '.zip', '.iso', 'turk']):continue

                            if 'ftp' in url: host = 'COV'; direct = True;
                            else: direct = False; host= 'turbobit.net'
                            #if not host in hostDict: continue

                            host = client.replaceHTMLCodes(host)
                            host = host.encode('utf-8')

                            sources.append({'source': host, 'quality': quality, 'language': 'en',
                                            'url': url, 'info': info, 'direct': direct, 'debridonly': True})

                        except:
                            pass
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


