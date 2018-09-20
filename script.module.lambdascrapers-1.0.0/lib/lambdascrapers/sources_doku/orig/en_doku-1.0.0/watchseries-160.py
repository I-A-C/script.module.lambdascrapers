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

import re,urllib,urlparse,json,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watchseriesfree.to','seriesfree.to']
        self.base_link = 'https://seriesfree.to/'
        self.search_link = 'https://seriesfree.to/search/%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            query = self.search_link % urllib.quote_plus(cleantitle.query(tvshowtitle))
            result = client.request(query)
            t = [tvshowtitle] + source_utils.aliases_to_array(aliases)
            t = [cleantitle.get(i) for i in set(t) if i]
            result = re.compile('itemprop="url"\s+href="([^"]+).*?itemprop="name"\s+class="serie-title">([^<]+)', re.DOTALL).findall(result)
            for i in result:
                if cleantitle.get(cleantitle.normalize(i[1])) in t and year in i[1]: url = i[0]

            url = url.encode('utf-8')
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.urljoin(self.base_link, url)
            result = client.request(url)

            title = cleantitle.get(title)
            premiered = re.compile('(\d{4})-(\d{2})-(\d{2})').findall(premiered)[0]
            premiered = '%s/%s/%s' % (premiered[2], premiered[1], premiered[0])
            items = dom_parser.parse_dom(result, 'a', attrs={'itemprop':'url'})

            url = [i.attrs['href'] for i in items if bool(re.compile('<span\s*>%s<.*?itemprop="episodeNumber">%s<\/span>' % (season,episode)).search(i.content))][0]
            
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            url = urlparse.urljoin(self.base_link, url)
            for i in range(3):
                result = client.request(url, timeout=10)
                if not result == None: break
            
            dom = dom_parser.parse_dom(result, 'div', attrs={'class':'links', 'id': 'noSubs'})
            result = dom[0].content
            
            links = re.compile('<tr\s*>\s*<td><i\s+class="fa fa-youtube link-logo"></i>([^<]+).*?href="([^"]+)"\s+class="watch',re.DOTALL).findall(result)         
            for link in links[:5]:
                try:
                    url2 = urlparse.urljoin(self.base_link, link[1])
                    for i in range(2):
                        result2 = client.request(url2, timeout=3)
                        if not result2 == None: break                    
                    r = re.compile('href="([^"]+)"\s+class="action-btn').findall(result2)[0]
                    valid, hoster = source_utils.is_host_valid(r, hostDict)
                    if not valid: continue
                    urls, host, direct = source_utils.check_directstreams(r, hoster)
                    for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                    
                except:
                    pass           
                    
            return sources
        except:
            return sources


    def resolve(self, url):
        return url

