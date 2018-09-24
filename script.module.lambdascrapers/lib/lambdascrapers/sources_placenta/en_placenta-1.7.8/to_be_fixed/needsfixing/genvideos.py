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


import re,json,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['genvideos.org', 'genvideos.com']
        self.base_link = 'https://genvideos.com/'
        self.search_link = '/results?q=%s'


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

            url = '/watch_%s.html' % v
            url = urlparse.urljoin(self.base_link, url)

            c = client.request(url, headers=h, output='cookie')
            c = client.request(urlparse.urljoin(self.base_link, '/av'), cookie=c, output='cookie', headers=h, referer=url)
            #c = client.request(url, cookie=c, headers=h, referer=url, output='cookie')

            post = urllib.urlencode({'v': v})
            u = urlparse.urljoin(self.base_link, '/video_info/frame')

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


