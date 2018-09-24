# NEEDS FIXING

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


import re,urllib,urlparse,json,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['tunemovie.net']
        self.base_link = 'http://tunemovie.net/'
        self.search_link = '/?type=movie&s=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link)
            query = query % urllib.quote_plus(title)

            t = cleantitle.get(title)

            r = client.request(query)

            r = client.parseDOM(r, 'div', attrs = {'class': 'thumb'})
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title'), re.findall('(\d{4})', i)) for i in r]
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]

            url = [i[0] for i in r if t in cleantitle.get(i[1]) and year == i[2]][0]
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            query = urlparse.urljoin(self.base_link, self.search_link)
            query = query % urllib.quote_plus(data['tvshowtitle'])

            t = cleantitle.get(data['tvshowtitle'])

            r = client.request(query)

            r = client.parseDOM(r, 'div', attrs = {'class': 'thumb'})
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title'), re.findall('(\d{4})', i)) for i in r]
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]

            url = [i[0] for i in r if t in cleantitle.get(i[1]) and ('Season %s' % season) in i[1]][0]
            url += '?episode=%01d' % int(episode)

            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            try:
                url, episode = re.findall('(.+?)\?episode=(\d*)$', url)[0]
            except:
                episode = None

            ref = url

            for i in range(3):
                result = client.request(url)
                if not result == None: break

            if not episode == None:
                result = client.parseDOM(result, 'div', attrs = {'id': 'ip_episode'})[0]
                ep_url = client.parseDOM(result, 'a', attrs = {'data-name': str(episode)}, ret='href')[0]
                for i in range(3):
                    result = client.request(ep_url)
                    if not result == None: break

            r = client.parseDOM(result, 'div', attrs = {'class': '[^"]*server_line[^"]*'})

            for u in r:
                try:
                    url = urlparse.urljoin(self.base_link, '/ip.file/swf/plugins/ipplugins.php')
                    p1 = client.parseDOM(u, 'a', ret='data-film')[0]
                    p2 = client.parseDOM(u, 'a', ret='data-server')[0]
                    p3 = client.parseDOM(u, 'a', ret='data-name')[0]
                    post = {'ipplugins': 1, 'ip_film': p1, 'ip_server': p2, 'ip_name': p3}
                    post = urllib.urlencode(post)
                    for i in range(3):
                        result = client.request(url, post=post, XHR=True, referer=ref, timeout='10')
                        if not result == None: break

                    result = json.loads(result)
                    u = result['s']
                    s = result['v']

                    url = urlparse.urljoin(self.base_link, '/ip.file/swf/ipplayer/ipplayer.php')

                    for n in range(3):
                        try:
                            post = {'u': u, 'w': '100%', 'h': '420', 's': s, 'n': n}
                            post = urllib.urlencode(post)
                            result = client.request(url, post=post, XHR=True, referer=ref)
                            src = json.loads(result)['data']

                            if type(src) is list:
                                src = [i['files'] for i in src]
                                for i in src:
                                    try:
                                        sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                                    except:
                                        pass
                            else:
                                src = client.request(src)
                                src = client.parseDOM(src, 'source', ret='src', attrs = {'type': 'video.+?'})[0]
                                src += '|%s' % urllib.urlencode({'User-agent': client.randomagent()})
                                sources.append({'source': 'cdn', 'quality': 'HD', 'language': 'en', 'url': src, 'direct': False, 'debridonly': False})
                        except:
                            pass
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return directstream.googlepass(url)


