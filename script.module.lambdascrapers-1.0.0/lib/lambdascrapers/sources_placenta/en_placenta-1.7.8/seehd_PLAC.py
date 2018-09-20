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
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['seehd.club', 'seehd.unblckd.bet', 'seehd.pl']
        self.base_link = 'https://seehd.one/'
        self.movie_link = '/%s-%04d-watch-online/'
        self.tvshow_link = '/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = cleantitle.geturl(title)
            url = urlparse.urljoin(self.base_link, self.movie_link %(t, int(year)))
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            t = cleantitle.geturl(tvshowtitle)
            url = urlparse.urljoin(self.base_link, self.tvshow_link %(t))
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url += '-s%02de%02d-watch-online/' % (int(season), int(episode))
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)
            if '<meta name="application-name" content="Unblocked">' in r: return sources
            r = client.parseDOM(r, 'div',attrs={'class':'entry-content'})[0]
            frames = []
            frames += client.parseDOM(r, 'iframe', ret='src')
            frames += client.parseDOM(r, 'a', ret='href')
            frames += client.parseDOM(r, 'source', ret='src')
            
            try:
                q = re.findall('<strong>Quality:</strong>([^<]+)', r)[0]
                if 'high' in q.lower(): quality = '720p'
                elif 'cam' in q.lower(): quality = 'CAM'
                else: quality = 'SD'
            except: quality = 'SD'
            
            for i in frames:
                try:
                    if 'facebook' in i or 'plus.google' in i: continue
                    url = i
                    if 'https://openload.co' in url and url.lower().endswith(('embed/%s')):
                        sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': url,
                                    'info': '', 'direct': False, 'debridonly': False})

                    elif 'ok.ru' in url:
                        print url
                        host = 'vk'
                        url = directstream.odnoklassniki(url)
                        print url
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': '', 'direct': False, 'debridonly': False})

                    elif 'vk.com' in url:
                        host = 'vk'
                        url = directstream.vk(url)
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': '', 'direct': False, 'debridonly': False})

                    else:
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        if valid:
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': '', 'direct': False, 'debridonly': False})
                        else:
                            valid, host = source_utils.is_host_valid(url, hostprDict)
                            if not valid: continue
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': '', 'direct': False, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

