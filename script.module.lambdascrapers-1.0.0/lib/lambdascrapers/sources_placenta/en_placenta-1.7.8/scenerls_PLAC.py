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
from resources.lib.modules import debrid
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['scene-rls.com','scene-rls.net']
        self.base_link = 'http://scene-rls.net/'
        self.search_link = '/?s=%s'
        self.search_link_2 = '/?s=%s&submit=Find'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('SceneRls - Exception: \n' + str(failure))
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
            log_utils.log('SceneRls - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            if debrid.status() == False: raise Exception()

            hostDict = hostprDict + hostDict

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            try:
                feed = True

                url = self.search_link % urllib.quote_plus(query)
                url = urlparse.urljoin(self.base_link, url)

                r = client.request(url)
                if r == None: feed = False

                posts = client.parseDOM(r, 'item')
                if not posts: feed = False

                items = []

                for post in posts:
                    try:
                        u = client.parseDOM(post, 'enclosure', ret='url')
                        u = [(i.strip('/').split('/')[-1], i) for i in u]
                        items += u
                    except:
                        pass
            except:
                pass

            try:
                if feed == True: raise Exception()

                url = self.search_link_2 % urllib.quote_plus(query)
                url = urlparse.urljoin(self.base_link, url)

                r = client.request(url)

                posts = client.parseDOM(r, 'div', attrs={'class': 'post'})

                items = [] ; dupes = []

                for post in posts:
                    try:
                        t = client.parseDOM(post, 'a')[0]
                        t = re.sub('<.+?>|</.+?>', '', t)

                        x = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', t)
                        if not cleantitle.get(title) in cleantitle.get(x): raise Exception()
                        y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', t)[-1].upper()
                        if not y == hdlr: raise Exception()

                        fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*)(\.|\)|\]|\s)', '', t.upper())
                        fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
                        fmt = [i.lower() for i in fmt]
                        if not any(i in ['1080p', '720p'] for i in fmt): raise Exception()

                        if len(dupes) > 2: raise Exception()
                        dupes += [x]

                        u = client.parseDOM(post, 'a', ret='href')[0]

                        r = client.request(u)
                        u = client.parseDOM(r, 'a', ret='href')
                        u = [(i.strip('/').split('/')[-1], i) for i in u]
                        items += u
                    except:
                        pass
            except:
                pass

            for item in items:
                try:
                    name = item[0]
                    name = client.replaceHTMLCodes(name)

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name)

                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()

                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()

                    if not y == hdlr: raise Exception()

                    quality,info = source_utils.get_release_quality(name, item[1])

                    url = item[1]
                    if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('SceneRls - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url


