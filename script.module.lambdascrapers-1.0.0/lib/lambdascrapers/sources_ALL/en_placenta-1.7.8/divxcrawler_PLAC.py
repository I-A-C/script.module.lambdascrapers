# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo


import re,urllib,urlparse

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
            url = urllib.urlencode(url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            imdb = data['imdb']

            try:
                query = urlparse.urljoin(self.base_link, self.search_link)
                result = client.request(query)
                m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result, re.DOTALL)
                m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
                if m:
                    link = m
                else:
                    query = urlparse.urljoin(self.base_link, self.search_link2)
                    result = client.request(query)
                    m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result, re.DOTALL)
                    m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
                    if m:
                        link = m
                    else:
                        query = urlparse.urljoin(self.base_link, self.search_link3)
                        result = client.request(query)
                        m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result, re.DOTALL)
                        m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
                        if m: link = m

            except:
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
                        pass

                    info = ' | '.join(info)

                    url = item[2]
                    if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                                    'direct': True, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url


