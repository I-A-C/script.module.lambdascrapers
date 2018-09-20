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
from bs4 import BeautifulSoup
import re

# Kudos to NIXGATES
class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'soaptv.me'
        self.base_link = 'https://soaptv.me/'
        self.search_link = 'https://soaptv.me/index.php?name=search'
        self.headers = {'referer':'https://soaptv.me'}


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle
            return url
        except:
            print("Unexpected error in SoapTV TVSHOW Script:", sys.exc_info()[0])
            return ""

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        with requests.Session() as s:
            try:
                sources = []
                data = {'do':'search','subaction':'search','story':(url + " season " + season),'all_word_search':'1'}
                p = s.post(self.search_link, data=data)
                soup = BeautifulSoup(p.text,'html.parser')
                p = soup.find_all('h2', {'class':'dtitle'})
                for i in p:
                    if re.sub(r'\W+', '', i.text.split('(')[0].lower()) == \
                            re.sub(r'\W+', '',((url + " season " + season).lower())):
                        p = (i.find_all('a')[0]['href'])
                p = s.get(p)
                soup = BeautifulSoup(p.text, 'html.parser')
                soup = soup.find_all('div', {'class':'fff6'})[0].find_all('a')
                if len(episode) == 1:
                    episode = "0"+episode

                for i in soup:
                    if ("e" + episode).lower() in i.text.lower():
                        url = (i['href'])
                p = s.get(url, headers = self.headers)
                sources.append(
                    {'source': 'depfile.us', 'quality': 'HD', 'language': 'en', 'url': p.url, 'direct': False, 'debridonly': True})
                return sources
            except Exception as e:
                print("Unexpected error in SoapTV episode Script:")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(exc_type, exc_tb.tb_lineno)
                return ""

    def sources(self, url, hostDict, hostprDict):
        return url

    def resolve(self, url):
            return url

#url = source.tvshow(source(), '', '', 'Vikings','','' '','2016')
#url = source.episode(source(),url,'', '', '', '', '4', '1')
#sources = source.sources(source(),url,'','')
