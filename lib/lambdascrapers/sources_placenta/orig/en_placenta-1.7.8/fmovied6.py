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

import re,traceback,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils
from resources.lib.modules import debrid

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['freemoviedownloads6.com']
        self.base_link = 'http://freemoviedownloads6.com/'
        self.search_link = '%s/search?q=freemoviedownloads6.com+%s+%s'
        self.goog = 'https://www.google.co.uk'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            scrape = title.lower().replace(' ','+').replace(':', '')

            start_url = self.search_link %(self.goog,scrape,year)

            html = client.request(start_url)
            results = re.compile('href="(.+?)"',re.DOTALL).findall(html)
            for url in results:
                if self.base_link in url:
                    if 'webcache' in url:
                        continue
                    if cleantitle.get(title) in cleantitle.get(url):
                        chkhtml = client.request(url)
                        chktitle = re.compile('<title>(.+?)</title>',re.DOTALL).findall(chkhtml)[0]
                        if cleantitle.get(title) in cleantitle.get(chktitle):
                            if year in chktitle:
                                return url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('FMovieD6 - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            if url == None: return
            sources = []
            html = client.request(url)
            html = html.split("type='video/mp4'")[1]
            match = re.compile('href="(.+?)"',re.DOTALL).findall(html)
            for link in match:
                if '1080' in link:
                    quality = '1080p'
                elif '720' in link:
                    quality = '720p'
                elif '480' in link:
                    quality = '480p'
                else:
                    quality = 'SD'
                if '.mkv' in link:
                    sources.append({'source': 'DirectLink', 'quality': quality, 'language': 'en', 'url': link, 'direct': True, 'debridonly': False})
                if '.mp4' in link:
                    sources.append({'source': 'DirectLink', 'quality': quality, 'language': 'en', 'url': link, 'direct': True, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('FMovieD6 - Exception: \n' + str(failure))
            return

    def resolve(self, url):
        return url