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

import requests
import sys
from resources.lib.modules import cleantitle
from bs4 import BeautifulSoup

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'myputlocker.me'
        self.base_link = 'http://myputlocker.me/'
        self.search_link = '/?s=%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle
        except:
            print("Unexpected error in Myputlock Script:", sys.exc_info()[0])
            return url
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            url = {'tvshowtitle': url, 'season': season, 'episode': episode}
            return url
        except:
            print("Unexpected error in Myputlock Script: episode", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            with requests.Session() as s:
                episode_link = "http://myputlocker.me/" + cleantitle.geturl(url['tvshowtitle']) + "-s" + url['season'] + "-e" + url[
                    'episode']
                p = s.get(episode_link)
                soup = BeautifulSoup(p.text, 'html.parser')
                iframes = soup.findAll('iframe')
                for i in iframes:
                    if 'thevideo' in i.get('src'):
                        sources.append(
                            {'source': "thevideo.me", 'quality': 'SD', 'language': "en", 'url': i['src'], 'info': '',
                             'direct': False, 'debridonly': False})
                    if 'openload' in i['src']:
                        sources.append(
                            {'source': "openload.co", 'quality': 'SD', 'language': "en", 'url': i['src'], 'info': '',
                             'direct': False, 'debridonly': False})
                    if 'vshare' in i['src']:
                        sources.append(
                            {'source': "vshare.eu", 'quality': 'SD', 'language': "en", 'url': i['src'], 'info': '',
                             'direct': False, 'debridonly': False})
            print(sources)
            return sources
        except:
            print("Unexpected error in Myputlock Script: source", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def resolve(self, url):
            return url