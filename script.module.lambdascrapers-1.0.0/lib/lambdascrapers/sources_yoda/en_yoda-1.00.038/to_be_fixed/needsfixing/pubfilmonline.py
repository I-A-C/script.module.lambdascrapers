# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Yoda
# Addon id: plugin.video.Yoda
# Addon Provider: MuadDib

import re,traceback,urllib,urlparse,json

from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import jsunpack
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['pubfilmonline.net']
        self.base_link = 'http://pubfilmonline.net/'
        self.post_link = '/wp-admin/admin-ajax.php'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url =  '%s/movies/%s-%s/' % (self.base_link, cleantitle.geturl(title),year)
            r = self.scraper.get(url).content
            if '<h2>ERROR <span>404</span></h2>' in r:
                url =  '%s/movies/%s/' % (self.base_link, cleantitle.geturl(title))
                r = self.scraper.get(url).content
                if '<h2>ERROR <span>404</span></h2>' in r: return
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('PubFilmOnline - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('PubFilmOnline - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('PubFilmOnline - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            if 'tvshowtitle' in data:
                url = '%s/episodes/%s-%01dx%01d/' % (self.base_link, cleantitle.geturl(data['tvshowtitle']), int(data['season']), int(data['episode']))
                year = re.findall('(\d{4})', data['premiered'])[0]
                r = self.scraper.get(url).content

                y = client.parseDOM(r, 'span', attrs = {'class': 'date'})[0]
                y = re.findall('(\d{4})', y)[0]
                if not y == year: raise Exception()
            else:
                r = self.scraper.get(url).content

            result = re.findall('''['"]file['"]:['"]([^'"]+)['"],['"]label['"]:['"]([^'"]+)''', r)

            for i in result:
                url = i[0].replace('\/', '/')
                sources.append({'source': 'gvideo', 'quality': source_utils.label_to_quality(i[1]), 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('PubFilmOnline - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        if 'google' in url:
            return directstream.googlepass(url)
        else:
            return url
