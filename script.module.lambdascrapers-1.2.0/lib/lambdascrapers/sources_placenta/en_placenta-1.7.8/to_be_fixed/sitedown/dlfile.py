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
import requests
import xbmc
from ..scraper import Scraper
from ..common import clean_title

class dlfile(Scraper):
    domains = ['http://dl.dlfile.pro/2/']
    name = "dlfile"
    sources = []

    def __init__(self):
        self.base_link = 'http://dl.dlfile.pro/2/'
                          
    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:
            start_url= self.base_link
            html = requests.get(start_url,timeout=5).content                               
            match = re.compile('<a href="(.+?)">(.+?)</a>').findall(html)                  
            for url,name in match:
                if name[0]==' ':
                    name = name[1:]
                name = name.replace('/','')
                url = self.base_link+url                                                 

                if title.lower().replace(' ','')==name.lower().replace(' ',''):          
                    
                    season_pull = "0%s"%season if len(season)<2 else season              
                    episode_pull = "0%s"%episode if len(episode)<2 else episode          
                    eppy_chec  = 'S%sE%s' %(season_pull,episode_pull)                    
                    
                    html2 = requests.get(url,timeout=5).content                          
                    match2 = re.compile('<a href="(.+?)"').findall(html2)                

                    for url2 in match2:
                        if eppy_chec in url2:                                            
                            url2 = url+'/'+url2                                          
                            print 'mecheck'+url2
                            if '1080p' in url2:                                         
                                qual = '1080p'
                            elif '720p' in url2: 
                                qual = '720p'
                            elif '480p' in url2:
                                qual = '480p'
                            else:
                                qual = 'SD'
                            self.sources.append({'source': 'Direct', 'quality': qual, 'scraper': self.name, 'url': url2,'direct': True})
            return self.sources
        except Exception as e:
            print repr(e)
            pass
            return []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            start_url= self.base_link
            html = requests.get(start_url,timeout=5).content 
            match = re.compile('<a href="(.+?)">(.+?)</a>').findall(html)
            for url,name in match:
                if '.20' in name:
                    name = name.split('20')[0]
                elif '.19' in name:
                    name = name.split('20')[0]
                else:pass
                if clean_title(title).lower()==clean_title(name).lower():
                    if year in url:
                        url = self.base_link+url
                        if '1080p' in url:                                          
                            qual = '1080p'
                        elif '720p' in url: 
                            qual = '720p'
                        elif '480p' in url:
                            qual = '480p'
                        else:
                            qual = 'SD'
                        self.sources.append({'source': 'Direct', 'quality': qual, 'scraper': self.name, 'url': url,'direct': True})
            return self.sources
        except Exception as e:
            print repr(e)
            pass
            return []                    
