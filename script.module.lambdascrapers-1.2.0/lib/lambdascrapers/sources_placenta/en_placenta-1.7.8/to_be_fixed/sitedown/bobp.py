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
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['bobmovies.pro']
        self.base_link = 'http://bobmovies.pro'
        self.search_link = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = title.lower()
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url  % (search_id.replace(':', '%3A').replace('&', '%26').replace("'", '%27').replace(' ', '+').replace('...', ' '))
            search_results = client.request(url)
            match = re.compile('<div id="post.+?href="(.+?)".+?title="(.+?)"',re.DOTALL).findall(search_results)
            for movie_url, movie_title in match:
                clean_title = cleantitle.get(title)
                movie_title = movie_title.replace('&#8230', ' ').replace('&#038', ' ').replace('&#8217', ' ').replace('...', ' ')
                clean_movie_title = cleantitle.get(movie_title)
                if clean_movie_title in clean_title:
                    return movie_url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('BobMoviesPro - movie - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            html = client.request(url)
            links = re.compile('<iframe width=".+?src="(.+?)"',re.DOTALL).findall(html)
            for link in links:
                quality,info = source_utils.get_release_quality(link, url)
                host = link.split('//')[1].replace('www.','')
                host = host.split('/')[0].split('.')[0].title()
                sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('BobMoviesPro - sources - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url