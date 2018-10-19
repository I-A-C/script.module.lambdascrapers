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

import re,traceback,base64,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['mydownloadtube.com','mydownloadtube.to']
        self.base_link = 'https://mydownloadtube.to/'
        self.search_link = '%ssearch/%s'
        self.download_link = '/movies/play_online'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = self.search_link % (self.base_link, urllib.quote_plus(title).replace('+', '-'))
            html = client.request(query, XHR=True)

            results = re.compile('<ul id=first-carousel1(.+?)</ul>',re.DOTALL).findall(html)
            result = re.compile('alt="(.+?)".+?<h2><a href="(.+?)".+?</h2>.+?>(.+?)</p>',re.DOTALL).findall(str(results))

            for found_title,url,date in result:
                new_url = self.base_link + url
                if cleantitle.get(title) in cleantitle.get(found_title):
                    if year in date:
                        return new_url
        except:
            failure = traceback.format_exc()
            log_utils.log('DLTube - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)
            mov_id = re.compile('id=movie value=(.+?)/>',re.DOTALL).findall(r)[0]
            mov_id = mov_id.rstrip()
            headers = {'Origin':'https://mydownloadtube.to', 'Referer':url,
                       'X-Requested-With':'XMLHttpRequest', 'User_Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
            request_url = 'https://mydownloadtube.to/movies/play_online' 
            form_data = {'movie':mov_id}
            links_page = client.request(request_url, headers=headers, post=form_data)
            matches = re.compile("sources:(.+?)controlbar",re.DOTALL).findall(links_page)
            match = re.compile("file:window.atob.+?'(.+?)'.+?label:\"(.+?)\"",re.DOTALL).findall(str(matches))
            for link,res in match:
                vid_url = base64.b64decode(link).replace(' ','%20')
                res = res.replace('3Dp','3D').replace(' HD','')
                sources.append({'source': 'DirectLink', 'quality': res, 'language': 'en', 'url': vid_url, 'info': '', 'direct': True, 'debridonly': False})

            match2 = re.compile('<[iI][fF][rR][aA][mM][eE].+?[sS][rR][cC]="(.+?)"',re.DOTALL).findall(links_page)
            for link in match2:
                host = link.split('//')[1].replace('www.','')
                host = host.split('/')[0].split('.')[0].title()
                if '1080' in link:
                    res='1080p'
                elif '720' in link:
                    res='720p'
                else:res = 'SD'
                if 'flashx' not in link:
                    sources.append({'source': host, 'quality': res, 'language': 'en', 'url': link, 'info': 'AC3', 'direct': False, 'debridonly': False})

            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('DLTube - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        try:
            url = client.request(url, output='geturl')
            return url
        except:
            return