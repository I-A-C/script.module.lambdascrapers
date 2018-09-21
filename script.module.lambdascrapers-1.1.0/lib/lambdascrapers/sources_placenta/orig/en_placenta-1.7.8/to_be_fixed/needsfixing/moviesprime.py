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
from resources.lib.modules import directstream
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['https://www.moviesprimeonline.site/']
        self.base_link = '/?s=%s'


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

            if not str(url).startswith('http'):

                data = urlparse.parse_qs(url)
                data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])


             
		url = '%s/%s-%s/' % (self.base_link, cleantitle.geturl(data['title']), data['year'])

                url = client.request(url, output='geturl')
                if url == None: raise Exception()

                r = client.request(url)

            else:
                url = urlparse.urljoin(self.base_link, url)

                r = client.request(url)

            links = client.parseDOM(r, 'iframe', ret='src')

            for link in links:
                try:                    
                    valid, hoster = source_utils.is_host_valid(link, hostDict)
                    if not valid: continue
                    urls, host, direct = source_utils.check_directstreams(link, hoster)
                    for x in urls:
                         if x['quality'] == 'SD':
                             try:                                 
                                 if 'HDTV' in x['url'] or '720' in  x['url']: x['quality'] = 'HD'
                                 if '1080' in  x['url']: x['quality'] = '1080p'
                             except:
                                 pass
                    sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
