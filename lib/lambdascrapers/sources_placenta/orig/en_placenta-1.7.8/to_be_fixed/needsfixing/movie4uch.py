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

import re,urlparse,urllib

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import dom_parser2
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movie4u.ch']
        self.base_link = 'https://movie4u.live/'
        self.search_link = '/?s=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
            r = client.request(search_url)
            r = client.parseDOM(r, 'div', {'class': 'result-item'})

            r = [(dom_parser2.parse_dom(i, 'a', req='href')[0],
                  client.parseDOM(i, 'img', ret='alt')[0],
                  dom_parser2.parse_dom(i, 'span', attrs={'class': 'year'})) for i in r]
            r = [(i[0].attrs['href'], i[1], i[2][0].content) for i in r if
                 (cleantitle.get(i[1]) == cleantitle.get(title) and i[2][0].content == year)]
            url = r[0][0]
    
            return url
        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(tvshowtitle)
            search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
            r = client.request(search_url)
            r = client.parseDOM(r, 'div', {'class': 'result-item'})
            r = [(dom_parser2.parse_dom(i, 'a', req='href')[0],
                  client.parseDOM(i, 'img', ret='alt')[0],
                  dom_parser2.parse_dom(i, 'span', attrs={'class': 'year'})) for i in r]
            r = [(i[0].attrs['href'], i[1], i[2][0].content) for i in r if
                 (cleantitle.get(i[1]) == cleantitle.get(tvshowtitle) and i[2][0].content == year)]
            url = source_utils.strip_domain(r[0][0])

            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            t = url.split('/')[2]
            url = self.base_link + '/episodes/%s-%dx%d' % (t, int(season), int(episode))
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = client.request(url)
            try:
                data = client.parseDOM(r, 'div', attrs={'class': 'playex'})
                data = [client.parseDOM(i, 'iframe', ret='src') for i in data if i]
                try:
                    for url in data[0]:
                        quality, info = source_utils.get_release_quality(url, None)
                        valid, host = source_utils.is_host_valid(url,hostDict)
                        if not valid: continue
                        host = host.encode('utf-8')
                        sources.append({
                            'source': host,
                            'quality': quality,
                            'language': 'en',
                            'url': url.replace('\/', '/'),
                            'direct': False,
                            'debridonly': False
                    })
                except:
                    pass
            except:
                pass

            return sources
        except Exception:
            return

    def resolve(self, url):

        return url