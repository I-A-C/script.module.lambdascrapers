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

import re,requests,sys,json,traceback,urllib,urlparse

from bs4 import BeautifulSoup
from resources.lib.modules import cleantitle
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:

    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'filepursuit.com'
        self.base_link = 'https://filepursuit.com/'
        self.search_link = '/search4/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'title': title, 'year': year}
            return url
        except:
            print("Unexpected error in Filepursuit Script: Movie", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle.replace(' ', '-')
        except:
            print("Unexpected error in Filepursuit Script: TV", sys.exc_info()[0])
            return url
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if len(episode) == 1: episode = "0" + episode
            if len(season) == 1: season = "0" + season
            url = {'tvshowtitle': url, 'season': season, 'episode': episode}
            return url
        except:
            print("Unexpected error in Filepursuit Script: episode", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            with requests.Session() as s:
                if 'episode' in url:
                    link = cleantitle.clean_search_query(url['tvshowtitle']) + ".s" + \
                       url['season'] + "e" + url['episode']
                else:
                    link = cleantitle.clean_search_query("%s.%s") % (url['title'], url['year'])
                p = s.get(self.search_link + link + "/type/videos")
                soup = BeautifulSoup(p.text, 'html.parser').find_all('table')[0]
                soup = soup.find_all('button')
                for i in soup:
                    fileUrl = i['data-clipboard-text']
                    source_check = self.link_check(fileUrl.lower(), re.sub('[^0-9a-zA-Z]+', '.', link).lower())
                    if source_check  != False:
                        hoster = fileUrl.split('/')[2]
                        quality = source_utils.check_sd_url(fileUrl)
                        sources.append({
                            'source': hoster,
                            'quality': quality,
                            'language': 'en',
                            'url': fileUrl,
                            'direct': False,
                            'debridonly': False,
                            'info':'FilePursuit App Available on the Play Store'
                        })
            return sources

        except:
            print("Unexpected error in Filepursuit Script: Sources", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return sources

    def resolve(self, url):
      return url

    def link_check(self, link, string):
        split = link.split('/')
        for i in split:
            if i.startswith(string):
                return link
        return False
