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

import re,urllib,urlparse,json,base64,time

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
        self.domains = ['kingmovies.to', 'kingmovies.is']
        self.base_link = 'https://kingmovies.is'
        self.search_link = '/search?q=%s'
        self.source_link = 'https://api.streamdor.co/sources'

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
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
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
            return

    def searchShow(self, title, season, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            cltitle = cleantitle.get(title+'season'+season)
            cltitle2 = cleantitle.get(title+'season%02d'%int(season))
            search = '%s Season %01d' % (title, int(season))
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(search)))
            r = client.request(url, timeout='15')
            r = [i[1] for i in re.findall(r'<li\s+class=["\']movie-item["\'].*?data-title=["\']([^"\']+)["\']><a\s+href=["\']([^"\']+)["\']',r, re.IGNORECASE) 
                 if cleantitle.get(re.sub(r"\s*\d{4}","",i[0])) in [cltitle, cltitle2]]

            if r == None: return
            else: url = r[0]

            return url
        except:
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            cltitle = cleantitle.get(title)
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(title)))
            r = client.request(url, timeout='15')
            r = [i[1] for i in re.findall(r'<li\s+class=["\']movie-item["\'].*?data-title=["\']([^"\']+)["\']><a\s+href=["\']([^"\']+)["\']',r, re.IGNORECASE) 
                 if cleantitle.get(re.sub(r"\s*\d{4}","",i[0])) == cltitle]

            if r == None: return
            else: url = r[0]
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                year = re.compile('(\d{4})-(\d{2})-(\d{2})').findall(data['premiered'])[0][0]
                episode = '%01d' % int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)

            else:
                episode = None
                year = data['year']
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            referer = url
            r = client.request(url)
            if episode == None:
                y = re.findall('Released\s*:\s*.+?\s*(\d{4})', r)[0]
                if not year == y: raise Exception()

            r = client.parseDOM(r, 'div', attrs = {'class': 'sli-name'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a'))

            if not episode == None:
                r = [i[0] for i in r if i[1].lower().startswith('episode %02d:' % int(data['episode'])) or i[1].lower().startswith('episode %d:' % int(data['episode']))]
            else:
                r = [i[0] for i in r]

            for u in r:
                try:
                    p = client.request(u, referer=referer, timeout='10')
                    quali = re.findall(r'Quality:\s*<.*?>([^<]+)',p)[0]
                    quali = quali if quali in ['HD', 'SD'] else source_utils.label_to_quality(quali)
                    src = re.findall('src\s*=\s*"(.*streamdor.co/video/\d+)"', p)[0]
                    if src.startswith('//'):
                        src = 'http:'+src
                    episodeId = re.findall('.*streamdor.co/video/(\d+)', src)[0]
                    p = client.request(src, referer=u)
                    try:
                        p = re.findall(r'JuicyCodes.Run\(([^\)]+)', p, re.IGNORECASE)[0]
                        p = re.sub(r'\"\s*\+\s*\"','', p)
                        p = re.sub(r'[^A-Za-z0-9+\\/=]','', p)    
                        p = base64.b64decode(p)                
                        p = jsunpack.unpack(p)
                        p = unicode(p, 'utf-8')
                    except:
                        continue

                    try:

                        fl = re.findall(r'file"\s*:\s*"([^"]+)',p)
                        if len(fl) > 0:
                            fl = fl[0]                                       
                            post = {'episodeID': episodeId, 'file': fl, 'subtitle': 'false', 'referer': urllib.quote_plus(u)}
                            p = client.request(self.source_link, post=post, referer=src, XHR=True)
                            js = json.loads(p)
                            src = js['sources']
                            p = client.request('http:'+src, referer=src)   
                            js = json.loads(p)[0]
                            ss = js['sources']
                            ss = [(i['file'], i['label']) for i in ss if 'file' in i]                        
                        
                        else:
                            try:
                                post = {'id': episodeId}
                                p2 = client.request('https://embed.streamdor.co/token.php?v=5', post=post, referer=src, XHR=True)
                                js = json.loads(p2)
                                tok = js['token']
                                p = re.findall(r'var\s+episode=({[^}]+});',p)[0]
                                js = json.loads(p)
                                ss = []
                                if 'eName' in js and js['eName'] != '':
                                    quali = source_utils.label_to_quality(js['eName'])
                                if 'fileEmbed' in js and js['fileEmbed'] != '':
                                    ss.append([js['fileEmbed'], quali])
                                if 'fileHLS' in js and js['fileHLS'] != '':
                                    ss.append(['https://hls.streamdor.co/%s%s'%(tok, js['fileHLS']), quali])  
                            except:
                                pass

                        for i in ss:
                            try: 
                                valid, hoster = source_utils.is_host_valid(i[0], hostDict)
                                direct = False
                                if not valid:
                                    hoster = 'CDN'                        
                                    direct = True                                       
                                sources.append({'source': hoster, 'quality': quali, 'language': 'en', 'url': i[0], 'direct': direct, 'debridonly': False})
                            except: pass

                    except:
                        url = re.findall(r'embedURL"\s*:\s*"([^"]+)',p)[0]
                        valid, hoster = source_utils.is_host_valid(url, hostDict)
                        if not valid: continue
                        urls, host, direct = source_utils.check_directstreams(url, hoster)
                        for x in urls:
                            sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})     

                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        if 'google' in url:
            return directstream.googlepass(url)
        else:
            return url
