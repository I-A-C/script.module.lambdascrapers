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

# FIXME: Some titles, such as Thor Ragnarok, cause exceptions and not pulling URL correct. Need to investigate.

import re,traceback,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watch32hd.co']
        self.base_link = 'https://watch32hd.co/'
        self.search_link = '/results/%s'
        self.watch_link = '/watch?v=%s_%s'  
		# Working: https://watch32hd.co/results?q=guardians+of+the+galaxy
		#   
		# https://watch32hd.co/watch?v=Guardians_Of_The_Galaxy_2014#video=ggvOQDQLiMEw0h2fAil9YwZbiUtwuMcBfCs1mQ_4
		# https://watch32hd.co/watch?v=Guardians_Of_The_Galaxy_2014

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('Watch32 - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title']
            year = data['year']

           #url = urlparse.urljoin(self.base_link, self.search_link) 
            url = urlparse.urljoin(self.base_link, self.watch_link) 

           #url = url % (title.replace(':', '').replace(' ','_'), year)
            url = url % (re.sub('[: \-]+','_',title), year)

            search_results = client.request(url)
            varid = re.compile('var frame_url = "(.+?)"',re.DOTALL).findall(search_results)[0].replace('/embed/','/streamdrive/info/')
            res_chk = re.compile('class="title"><h1>(.+?)</h1>',re.DOTALL).findall(search_results)[0]
            varid = 'http:'+varid
            holder = client.request(varid)
            links = re.compile('"src":"(.+?)"',re.DOTALL).findall(holder)
            for link in links:
                vid_url = link.replace('\\','')
                if '1080' in res_chk:
                    quality = '1080p'
                elif '720' in res_chk:
                    quality = '720p'
                else:
                    quality = 'DVD'
                sources.append({'source': 'Googlelink', 'quality': quality, 'language': 'en', 'url': vid_url, 'direct': False, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('Watch32 - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url