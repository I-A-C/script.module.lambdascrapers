# -*- coding: UTF-8 -*-
'''
    coolmoviezone scraper for Exodus forks.
    Nov 9 2018 - Checked

    Updated and refactored by someone.
    Originally created by others.
'''
import re,traceback,urllib,urlparse
import resolveurl

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['coolmoviezone.biz']
        self.base_link = 'http://coolmoviezone.biz/'
        self.search_link = '/index.php?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url  % (title.replace(':', ' ').replace(' ', '+'))

            search_results = client.request(url)
            match = re.compile('<h1><a href="(.+?)" rel="bookmark">(.+?)</a></h1>',re.DOTALL).findall(search_results)
            for item_url,item_title in match:
                if cleantitle.get(title) in cleantitle.get(item_title):
                    if year in str(item_title):
                        return item_url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('CoolMovieZone - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            html = client.request(url)
            Links = re.compile('<td align="center"><strong><a href="(.+?)"',re.DOTALL).findall(html)
            for link in Links:
                host = link.split('//')[1].replace('www.','')
                host = host.split('/')[0].split('.')[0].title()
                sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('CoolMovieZone - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
