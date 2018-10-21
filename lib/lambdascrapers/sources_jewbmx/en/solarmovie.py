# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################
# -Cleaned and Checked on 10-11-2018 by JewBMX in Yoda.

import re,traceback,urllib,urlparse,hashlib,random,string,json,base64,sys,xbmc,resolveurl

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['solarmovie.ms']
        self.base_link = 'http://www.solarmovie.ms'
        self.search_link = '/keywords/%s'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = title.lower().replace(':', ' ').replace('-', ' ')

            start_url = urlparse.urljoin(self.base_link, (self.search_link % (search_id.replace(' ','%20'))))         
            
            headers={'User-Agent':client.randomagent()}
            html = client.request(start_url,headers=headers)     
            
            match = re.compile('<span class="name"><a title="(.+?)" href="(.+?)".+?title="(.+?)"',re.DOTALL).findall(html)
            for name,item_url, link_year in match:
                if year in link_year:                                                        
                    if cleantitle.get(title) in cleantitle.get(name):
                        return item_url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('SolarMovie - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            headers={'User-Agent':client.randomagent()}
            html = client.request(url,headers=headers)

            Links = re.compile('id="link_.+?target="_blank" id="(.+?)"',re.DOTALL).findall(html)
            for vid_url in Links:
                if 'openload' in vid_url:
                    try:
                        source_html   = client.request(vid_url,headers=headers)
                        source_string = re.compile('description" content="(.+?)"',re.DOTALL).findall(source_html)[0]
                        quality,info = source_utils.get_release_quality(source_string, vid_url)
                    except:
                        quality = 'DVD'
                        info = []
                    sources.append({'source': 'Openload','quality': quality,'language': 'en','url':vid_url,'info':info,'direct': False,'debridonly': False})
                elif 'streamango' in vid_url:
                    try:  
                        source_html = client.request(vid_url,headers=headers)
                        source_string = re.compile('description" content="(.+?)"',re.DOTALL).findall(source_html)[0]
                        quality,info = source_utils.get_release_quality(source_string, vid_url)  
                    except:
                        quality = 'DVD'
                        info = []
                    sources.append({'source': 'Streamango','quality': quality,'language': 'en','url':vid_url,'info':info,'direct': False,'debridonly': False})
                else:
                    if resolveurl.HostedMediaFile(vid_url):
                        quality,info = source_utils.get_release_quality(vid_url, vid_url)  
                        host = vid_url.split('//')[1].replace('www.','')
                        host = host.split('/')[0].split('.')[0].title()
                        sources.append({'source': host,'quality': quality,'language': 'en','url':vid_url,'info':info,'direct': False,'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('SolarMovie - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url