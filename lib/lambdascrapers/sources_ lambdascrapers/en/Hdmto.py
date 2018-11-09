# -*- coding: UTF-8 -*-
'''
    hdmto scraper for Exodus forks.
    Nov 9 2018 - Checked

    Updated and refactored by someone.
    Originally created by others.
'''
import re
import urllib
import urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import proxy


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['hdm.to']
        self.base_link = 'https://hdm.to'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = cleantitle.geturl(title)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            url = '%s/%s/' % (self.base_link,url)
            r = client.request(url)
            try:
                match = re.compile('<iframe.+?src="(.+?)"').findall(r)
                for url in match:
                    sources.append({'source': 'Openload.co','quality': '1080p','language': 'en','url': url,'direct': False,'debridonly': False}) 
            except:
                return
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url
