# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: MuadDib


import re,traceback,urllib,urlparse,json,base64,time,xbmc

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import directstream
from resources.lib.modules import source_utils
from resources.lib.modules import jsunpack

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cmovieshd.net']
        self.base_link = 'http://cmovieshd.net/'
        self.search_link = 'search/?q=%s'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('CMoviesHD - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('CMoviesHD - Exception: \n' + str(failure))
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
            log_utils.log('CMoviesHD - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, locDict):
        sources = []

        try:
            if url == None: return sources
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            aliases = eval(data['aliases'])
            #cookie = '; approve_search=yes'
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)
            result = client.request(query) #, cookie=cookie)
            try:

                if 'episode' in data:
                    r = client.parseDOM(result, 'div', attrs={'class': 'ml-item'})
                    r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
                    r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d+)', i[1])) for i in r]
                    r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
                    url = [i[0] for i in r if self.matchAlias(i[2][0], aliases) and i[2][1] == data['season']][0]

                    url = '%swatch' % url
                    result = client.request(url)

                    url = re.findall('a href=\"(.+?)\" class=\"btn-eps first-ep \">Episode %02d' % int(data['episode']), result)[0]

                else:
                    r = client.parseDOM(result, 'div', attrs={'class': 'ml-item'})
                    r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
                    results = [(i[0], i[1], re.findall('\((\d{4})', i[1])) for i in r]
                    try:
                        r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
                        url = [i[0] for i in r if self.matchAlias(i[1], aliases) and (year == i[2])][0]
                    except:
                        url = None
                        pass

                    if (url == None):
                        url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]
                    url = '%s/watch' % url

                url = client.request(url, output='geturl')
                if url == None: raise Exception()

            except:
              return sources

            url = url if 'http' in url else urlparse.urljoin(self.base_link, url)
            result = client.request(url)
            src = re.findall('src\s*=\s*"(.*streamdor.co\/video\/\d+)"', result)[0]
            if src.startswith('//'):
                src = 'http:'+src
            episodeId = re.findall('.*streamdor.co/video/(\d+)', src)[0]
            p = client.request(src, referer=url)
            try:
                p = re.findall(r'JuicyCodes.Run\(([^\)]+)', p, re.IGNORECASE)[0]
                p = re.sub(r'\"\s*\+\s*\"','', p)
                p = re.sub(r'[^A-Za-z0-9+\\/=]','', p)
                p = base64.b64decode(p)
                p = jsunpack.unpack(p)
                p = unicode(p, 'utf-8')

                post = {'id': episodeId}
                p2 = client.request('https://embed.streamdor.co/token.php?v=5', post=post, referer=src, XHR=True)
                js = json.loads(p2)
                tok = js['token']
                quali = 'SD'
                try:
                    quali = re.findall(r'label:"(.*?)"',p)[0]
                except:
                    pass
                p = re.findall(r'var\s+episode=({[^}]+});',p)[0]
                js = json.loads(p)
                ss = []

                #if 'eName' in js and js['eName'] != '':
                #    quali = source_utils.label_to_quality(js['eName'])
                if 'fileEmbed' in js and js['fileEmbed'] != '':
                    ss.append([js['fileEmbed'], quali])
                if 'fileHLS' in js and js['fileHLS'] != '':
                    ss.append(['https://hls.streamdor.co/%s%s'%(tok, js['fileHLS']), quali])
            except:
                return sources

            for link in ss:

                try:
                    if 'google' in url:
                        valid, hoster = source_utils.is_host_valid(url, hostDict)
                        urls, host, direct = source_utils.check_directstreams(url, hoster)
                        for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})

                    else:
                        try:
                            valid, hoster = source_utils.is_host_valid(link[0], hostDict)
                            direct = False
                            if not valid:
                                hoster = 'CDN'
                                direct = True
                            sources.append({'source': hoster, 'quality': link[1], 'language': 'en', 'url': link[0], 'direct': direct, 'debridonly': False})
                        except: pass

                except:
                    pass

            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('CMoviesHD - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        if 'google' in url:
            return directstream.googlepass(url)
        else:
            return url
