# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Mr.Blamo
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: K1ept0

import re,traceback,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['www.timetowatch.video']
        self.base_link = 'https://www.timetowatch.video'
        self.search_link = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = title.lower()
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url  % (search_id.replace(':', '%3A').replace(',', '%2C').replace('&', '%26').replace("'", '%27').replace(' ', '+').replace('...', ' '))
            search_results = client.request(url)
            match = re.compile('<div data-movie-id=.+?href="(.+?)".+?oldtitle="(.+?)"',re.DOTALL).findall(search_results)
            for movie_url, movie_title in match:
                clean_title = cleantitle.get(title)
                movie_title = movie_title.replace('&#8230', ' ').replace('&#038', ' ').replace('&#8217', ' ').replace('...', ' ')
                clean_movie_title = cleantitle.get(movie_title)
                if clean_movie_title in clean_title:
                    return movie_url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('Timewatch - Movie - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            html = client.request(url)
            links = re.compile('<form id="linkplayer.+?href="(.+?)"',re.DOTALL).findall(html)
            for link in links:
                quality,info = source_utils.get_release_quality(link, url)
                host = link.split('//')[1].replace('www.','')
                host = host.split('/')[0].split('.')[0].title()
                sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('Timewatch - Sources - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url