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


import re,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['dizigold.net', 'dizigold1.com']
        self.base_link = 'http://www.dizigold2.com'
        self.player_link = 'http://player.dizigold2.com/?id=%s&s=1&dil=%s'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            result = cache.get(self.dizigold_tvcache, 120)

            tvshowtitle = cleantitle.get(tvshowtitle)

            result = [i[0] for i in result if tvshowtitle == i[1]][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def dizigold_tvcache(self):
        try:
            result = client.request(self.base_link)
            result = client.parseDOM(result, 'div', attrs = {'class': 'dizis'})[0]
            result = re.compile('href="(.+?)">(.+?)<').findall(result)
            result = [(re.sub('http.+?//.+?/','/', i[0]), re.sub('&#\d*;','', i[1])) for i in result]
            result = [(i[0], cleantitle.get(i[1])) for i in result]

            return result
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if url == None: return

        url = '/%s/%01d-sezon/%01d-bolum' % (url.replace('/', ''), int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            base_url = urlparse.urljoin(self.base_link, url)

            result = client.request(base_url)
            id = re.compile('var\s*view_id\s*=\s*"(\d*)"').findall(result)[0]


            for dil in ['tr', 'or', 'en']:
                query = self.player_link % (id, dil)

                result = client.request(query, referer=base_url)

                try:
                    url = client.parseDOM(result, 'iframe', ret='src')[-1]

                    if 'openload' in url:
                        host = 'openload.co' ; direct = False ; url = [{'url': url, 'quality': 'HD'}]

                    elif 'ok.ru' in url:
                        host = 'vk' ; direct = True ; url = directstream.odnoklassniki(url)

                    elif 'vk.com' in url:
                        host = 'vk' ; direct = True ; url = directstream.vk(url)

                    else: raise Exception()

                    for i in url: sources.append({'source': host, 'quality': i['quality'], 'language': 'en', 'url': i['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

                try:
                    url = re.compile('"?file"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?"').findall(result)

                    links = [(i[0], '1080p') for i in url if int(i[1]) >= 1080]
                    links += [(i[0], 'HD') for i in url if 720 <= int(i[1]) < 1080]
                    links += [(i[0], 'SD') for i in url if 480 <= int(i[1]) < 720]

                    for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'language': 'en', 'url': i[0], 'direct': True, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


