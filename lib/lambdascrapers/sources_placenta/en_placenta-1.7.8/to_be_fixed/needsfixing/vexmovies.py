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

import re,traceback,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vexmovies.org']
        self.base_link = 'http://vexmovies.org'
        self.search_link = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url  % (title.replace(':', ' ').replace(' ', '+'))

            search_results = client.request(url)
            match = re.compile('class="item".+?href="(.+?)".+?alt="(.+?)".+?class="year">(.+?)</span>',re.DOTALL).findall(search_results)
            for item_url,item_title,date in match:
                if cleantitle.get(title) in cleantitle.get(item_title):
                    if year in str(date):
                        return item_url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('VexMovies - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            html = client.request(url)

            source = re.compile('<iframe src="(.+?)"',re.DOTALL).findall(html)[0]
            if 'consistent.stream' in source:
                html = client.request(source)
                page = re.compile(""":title=["'](.+?)["']\>""").findall(html)[0]
                decode = client.replaceEscapeCodes(page)
                links = re.compile('"sources.+?"(http.+?)"',re.DOTALL).findall(decode)
                for link in links:
                    link = link.replace('\\','')
                    if '1080' in link:
                        quality='1080p'
                    elif '720' in link:
                        quality = '720p'
                    else:
                        quality = 'DVD'
                    host = link.split('//')[1].replace('www.','')
                    host = host.split('/')[0].split('.')[0].title()
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('VexMovies - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url