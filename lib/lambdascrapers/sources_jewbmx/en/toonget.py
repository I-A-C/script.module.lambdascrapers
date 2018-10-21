# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 10-11-2018 by JewBMX in Yoda.

import re,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import proxy


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['toonget.net']
        self.base_link = 'https://toonget.net'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = '%s %s' % (title,year)
            return url
        except:
            return
			
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = cleantitle.geturl(tvshowtitle)
            return url
        except:
            return
 
    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            if season == '1': 
                url = self.base_link + '/' + url + '-episode-' + episode
            else:
                url = self.base_link + '/' + url + '-season-' + season + '-episode-' + episode
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = client.request(url)
            try:
                match = re.compile('Playlist .+?</span></div><div><iframe src="(.+?)"').findall(r)
                for url in match: 
                    r = client.request(url)
                    if 'playpanda' in url:
                        match = re.compile("url: '(.+?)',").findall(r)
                    else:
                        match = re.compile('file: "(.+?)",').findall(r)
                    for url in match: 
                        sources.append({'source': 'Direct','quality': 'SD','language': 'en','url': url,'direct': False,'debridonly': False}) 
            except:
                return
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url