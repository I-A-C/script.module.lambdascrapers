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

# FIXME: Site Search appears boken, need to add tv show support, and is movies even on this site?

import re,traceback,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import proxy
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['project-free-tv.ch','project-free-tv.ag']
        self.base_link = 'http://project-free-tv.ag'
        self.search_link = '/movies/%s-%s/'
        self.search_link_2 = '/movies/search-form/?free=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.search_link % (cleantitle.geturl(title), year)

            q = urlparse.urljoin(self.base_link, url)

            r = proxy.geturl(q)
            if not r == None: return url

            t = cleantitle.get(title)

            q = self.search_link_2 % urllib.quote_plus(cleantitle.query(title))
            q = urlparse.urljoin(self.base_link, q)

            r = client.request(q)

            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a'))
            r = [(i[0], re.findall('(?:\'|\")(.+?)(?:\'|\")', i[1])) for i in r]
            r = [(i[0], [re.findall('(.+?)\((\d{4})', x) for x in i[1]]) for i in r]
            r = [(i[0], [x[0] for x in i[1] if x]) for i in r]
            r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if i[1]]
            r = [i[0] for i in r if t == cleantitle.get(i[1]) and year == i[2]]

            url = re.findall('(?://.+?|)(/.+)', r[0])[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('ProjectFree - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            r = proxy.request(url, 'movies')

            links = client.parseDOM(r, 'tr')

            for i in links:
                try:
                    url = re.findall('callvalue\((.+?)\)', i)[0]
                    url = re.findall('(http.+?)(?:\'|\")', url)[0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')

                    quality = re.findall('quality(\w+)\.png', i)[0]
                    if quality == 'CAM' in i or quality == 'TS': quality = 'CAM'
                    else: quality = 'SD'

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            filter = [i for i in sources if i['quality'] == 'SD']
            if filter: sources = filter

            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('ProjectFree - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url