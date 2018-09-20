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


import re,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import dom_parser2

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['rjsmovie.co']
        self.base_link = 'https://www.rjsmovie.co'
        self.search_link = 'movies/%s/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            query = (self.search_link % (clean_title))
            url = urlparse.urljoin(self.base_link, query)
            return url
        except Exception:
            return
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []          
            r = client.request(url)
            r = dom_parser2.parse_dom(r, 'div', {'id': re.compile('option-\d+')})
            r = [dom_parser2.parse_dom(i, 'iframe', req=['src']) for i in r if i]
            r = [(i[0].attrs['src']) for i in r if i]
            if r:
                for url in r:
                    try:
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                        if host in hostDict:
                            host = client.replaceHTMLCodes(host)
                            host = host.encode('utf-8')
                            sources.append({
                                'source': host,
                                'quality': 'SD',
                                'language': 'en',
                                'url': url.replace('\/','/'),
                                'direct': False,
                                'debridonly': False
                            })
                    except: pass
            return sources
        except Exception:
            return

    def resolve(self, url):
        return url
