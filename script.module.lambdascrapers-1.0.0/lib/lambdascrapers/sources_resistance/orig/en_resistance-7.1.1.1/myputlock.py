# -*- coding: UTF-8 -*-
#           ________
#          _,.-Y  |  |  Y-._
#      .-~"   ||  |  |  |   "-.
#      I" ""=="|" !""! "|"[]""|     _____
#      L__  [] |..------|:   _[----I" .-{"-.
#     I___|  ..| l______|l_ [__L]_[I_/r(=}=-P
#    [L______L_[________]______j~  '-=c_]/=-^
#     \_I_j.--.\==I|I==_/.--L_]
#       [_((==)[`-----"](==)j
#          I--I"~~"""~~"I--I
#          |[]|         |[]|
#          l__j         l__j
#         |!!|         |!!|
#          |..|         |..|
#          ([])         ([])
#          ]--[         ]--[
#          [_L]         [_L]
#         /|..|\       /|..|\
#        `=}--{='     `=}--{='
#       .-^--r-^-.   .-^--r-^-.
# Resistance is futile @lock_down... 

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