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
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['filmfrantic.com']
        self.base_link = 'http://filmfrantic.com'
        self.search_link = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url  % (title.replace(':', ' ').replace(' ', '+'))

            search_results = client.request(url)
            match = re.compile('<article id=.+?href="(.+?)" title="(.+?)"',re.DOTALL).findall(search_results)
            for row_url, row_title in match:
                if cleantitle.get(title) in cleantitle.get(row_title):
                    if year in str(row_title):
                        return row_url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('FilmFrantic - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            html = client.request(url)

            links = re.compile(' <iframe src="(.+?)"',re.DOTALL).findall(html)

            for link in links:
                if '1080' in link:
                    quality = '1080p'
                elif '720' in link:
                    quality = '720p'
                else:
                    quality = 'SD'
                host = link.split('//')[1].replace('www.','')
                host = host.split('/')[0].split('.')[0].title()
                sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('FilmFrantic - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url