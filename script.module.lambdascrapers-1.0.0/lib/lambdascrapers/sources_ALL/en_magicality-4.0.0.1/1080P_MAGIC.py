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

import re,traceback,urllib,urlparse,json,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['1080pmovie.com', 'watchhdmovie.net']
        self.base_link = 'https://watchhdmovie.net'
        self.search_link = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('1080PMovies - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None: return
            urldata = urlparse.parse_qs(url)
            urldata = dict((i, urldata[i][0]) for i in urldata)
            title = urldata['title'].replace(':', ' ').lower()
            year = urldata['year']

            search_id = title.lower()
            start_url = self.search_link % (self.base_link, search_id.replace(' ','%20'))

            headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
            html = client.request(start_url,headers=headers)
            Links = re.compile('"post","link":"(.+?)","title".+?"rendered":"(.+?)"',re.DOTALL).findall(html)
            for link,name in Links:
                link = link.replace('\\','')
                if title.lower() in name.lower(): 
                    if year in name:
                        holder = client.request(link,headers=headers)
                        new = re.compile('<iframe src="(.+?)"',re.DOTALL).findall(holder)[0]
                        end = client.request(new,headers=headers)
                        final_url = re.compile('<iframe src="(.+?)"',re.DOTALL).findall(end)[0]
                        valid, host = source_utils.is_host_valid(final_url, hostDict)
                        sources.append({'source':host,'quality':'1080p','language': 'en','url':final_url,'info':[],'direct':False,'debridonly':False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('1080PMovies - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return directstream.googlepass(url)

