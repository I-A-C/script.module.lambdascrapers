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
from resources.lib.modules import control

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['rlsbb.com', 'rlsbb.ru']
        self.base_link = 'http://rlsbb.ru'
        self.search_base_link = 'http://search.rlsbb.ru'
        self.search_cookie = 'serach_mode=rlsbb'
        self.search_link = '/lib/search526049.php?phrase=%s&pindex=1&content=true'
        self.search_link2 = '/search/%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            if debrid.status() == False: raise Exception()


            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']


            posts = []

            if 'tvshowtitle' in data:
                query = '%s S%02d' % (data['tvshowtitle'], int(data['season']))
                query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

                referer = self.search_link2 % urllib.quote_plus(query)
                referer = urlparse.urljoin(self.search_base_link, referer)

                url = self.search_link % urllib.quote_plus(query)
                url = urlparse.urljoin(self.search_base_link, url)

                result = client.request(url, cookie=self.search_cookie, XHR=True, referer=referer)
                try: posts += json.loads(re.findall('({.+?})$', result)[0])['results']
                except: pass

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            referer = self.search_link2 % urllib.quote_plus(query)
            referer = urlparse.urljoin(self.search_base_link, referer)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.search_base_link, url)

            result = client.request(url, cookie=self.search_cookie, XHR=True, referer=referer)
            try: posts += json.loads(re.findall('({.+?})$', result)[0])['results']
            except: pass


            links = [] ; dupes = []

            for post in posts:
                try:
                    name = post['post_title'] ; url = post['post_name']

                    if url in dupes: raise Exception()
                    dupes.append(url)

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name)

                    if not cleantitle.get(title) in cleantitle.get(t): raise Exception()

                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()

                    if y.isdigit(): cat = 'movie'
                    elif 'S' in y and 'E' in y: cat = 'episode'
                    elif 'S' in y: cat = 'tvshow'

                    if cat == 'movie': hdlr = data['year']
                    elif cat == 'episode': hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode']))
                    elif cat == 'tvshow': hdlr = 'S%02d' % int(data['season'])

                    if not y == hdlr: raise Exception()


                    items = []

                    content = post['post_content']

                    try: items += zip([i for i in client.parseDOM(content, 'p') if 'Release Name:' in i], [i for i in client.parseDOM(content, 'p') if '<strong>Download' in i])
                    except: pass

                    try: items += client.parseDOM(content, 'p', attrs = {'style': '.+?'})
                    except: pass

                    for item in items:
                        try:
                            if type(item) == tuple: item = '######URL######'.join(item)

                            fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*)(\.|\)|\]|\s)', '', name.upper())
                            fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
                            fmt = [i.lower() for i in fmt]

                            if any(i.endswith(('subs', 'sub', 'dubbed', 'dub')) for i in fmt): raise Exception()
                            if any(i in ['extras'] for i in fmt): raise Exception()

                            if '1080p' in fmt: quality = '1080p'
                            elif '720p' in fmt: quality = 'HD'
                            else: quality = 'SD'
                            if any(i in ['dvdscr', 'r5', 'r6'] for i in fmt): quality = 'SCR'
                            elif any(i in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'telesync', 'ts'] for i in fmt): quality = 'CAM'

                            info = []

                            if '3d' in fmt: info.append('3D')

                            try:
                                if cat == 'tvshow': raise Exception()
                                size = re.findall('(\d+(?:\.|/,|)\d+(?:\s+|)(?:GB|GiB|MB|MiB))', item)[0].strip()
                                div = 1 if size.endswith(('GB', 'GiB')) else 1024
                                size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                                size = '%.2f GB' % size
                                info.append(size)
                            except:
                                pass

                            info = ' | '.join(info)

                            url = item.rsplit('######URL######')[-1]
                            url = zip(client.parseDOM(url, 'a'), client.parseDOM(url, 'a', ret='href'))

                            for i in url: links.append({'url': i[1], 'quality': quality, 'info': info, 'host': i[0], 'cat': cat})
                        except:
                            pass

                except:
                    pass


            check = [i for i in links if not i['quality'] == 'CAM']
            if len(check) > 0: links = check

            hostDict = hostprDict + hostDict

            for i in links:
                try:
                    url = i['url']
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    if i['cat'] == 'tvshow':
                        if not i['quality'] in ['1080p', 'HD']: raise Exception()
                        if not any(i['host'].lower() in x for x in hostDict): raise Exception()
                        url = client.request(url)
                        url = client.parseDOM(url, 'ol')[0]
                        url = client.parseDOM(url, 'div', attrs = {'style': '.+?'})[int(data['episode'])-1]

                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': i['quality'], 'language': 'en', 'url': url, 'info': i['info'], 'direct': False, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


