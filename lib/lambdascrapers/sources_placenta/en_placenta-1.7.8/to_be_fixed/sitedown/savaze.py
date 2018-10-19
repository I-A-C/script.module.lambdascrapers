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
import re
import urllib
import urlparse
import json
import base64

from resources.lib.modules import client, cleantitle, directstream, dom_parser2, source_utils, log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['savaze.com']
        self.base_link = 'http://www.savaze.com'
        self.movies_search_path = ('links/%s')

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            urls = []
            
            lst = ['1080p','720p','bluray-2','bluray']
            
            for i in lst:
                url = urlparse.urljoin(self.base_link, self.movies_search_path % (imdb) + '-%s' % i)
                r = client.request(url)
                if r: urls.append(url)

            url = urlparse.urljoin(self.base_link, self.movies_search_path % (imdb))
            url = client.request(url, output='geturl')
            if '-1080p' not in url and '-720p' not in url and '-bluray' not in url:
                r = client.request(url)
                if r: urls.append(url)

            if not urls: return
            
            return urls
        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return ''

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            urls = []
            
            lst = ['1080p','720p','bluray-2','bluray']
            clean_season = season if len(season) >= 2 else '0' + season
            clean_episode = episode if len(episode) >= 2 else '0' + episode

            for i in lst:
                url = urlparse.urljoin(self.base_link, self.movies_search_path % (imdb) + '-s%se%s-%s' % (clean_season, clean_episode, i))
                r = client.request(url)
                if r: urls.append(url)

            url = urlparse.urljoin(self.base_link, self.movies_search_path % (imdb))
            url = client.request(url, output='geturl')
            if '-1080p' not in url and '-720p' not in url and '-bluray' not in url:
                r = client.request(url)
                if r: urls.append(url)

            if not urls: return
            return urls
        except Exception:
            return
            
    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            for u in url:
                hostDict += [('clicknupload.org')]
                quality = '1080p' if '-1080p' in u or 'bluray-2' in u else '720p' if '-720p' in u or 'bluray' in u else 'SD'
                
                r = client.request(u)
                r = dom_parser2.parse_dom(r, 'ul', {'class': 'download-links'})
                r = dom_parser2.parse_dom(r, 'a', req=['href'])
                r = [i.attrs['href'] for i in r if i]
                for i in r:
                    try:
                        valid, host = source_utils.is_host_valid(i, hostDict)
                        if not valid: continue
                        sources.append({
                            'source': host,
                            'quality': quality,
                            'language': 'en',
                            'url': i,
                            'direct': False,
                            'debridonly': False
                        })
                    except: pass
            return sources
        except Exception:
            return
            
    def resolve(self, url):
       return url
