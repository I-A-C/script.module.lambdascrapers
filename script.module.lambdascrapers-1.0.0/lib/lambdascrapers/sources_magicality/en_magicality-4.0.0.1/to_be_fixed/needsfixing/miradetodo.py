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


import re,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['miradetodo.io']
        self.base_link = 'http://miradetodo.io'
        self.search_link = '/?s=%s'
        self.episode_link = '/episodio/%s-%sx%s'
        self.tvshow_link = '/series/%s/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language': 'es-AR'})
            t = client.parseDOM(t, 'title')[0]
            t = re.sub('(?:\(|\s)\d{4}.+', '', t).strip().encode('utf-8')

            q = self.search_link % urllib.quote_plus(t)
            q = urlparse.urljoin(self.base_link, q)

            r = client.request(q)

            r = client.parseDOM(r, 'div', attrs = {'class': 'item'})
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'span', attrs = {'class': 'tt'}), client.parseDOM(i, 'span', attrs = {'class': 'year'})) for i in r]
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            r = [i[0] for i in r if cleantitle.get(t) == cleantitle.get(i[1]) and year == i[2]][0]

            url = re.findall('(?://.+?|)(/.+)', r)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            pass

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            t = cleantitle.geturl(tvshowtitle)

            q = self.tvshow_link % t
            q = urlparse.urljoin(self.base_link, q)
            r = client.request(q, output='geturl')

            if not r:
                t = 'http://www.imdb.com/title/%s' % imdb
                t = client.request(t, headers={'Accept-Language': 'es-AR'})
                t = client.parseDOM(t, 'title')[0]
                t = re.sub('(?:\(|\s)\(TV Series.+', '', t).strip().encode('utf-8')

                q = self.search_link % urllib.quote_plus(t)
                q = urlparse.urljoin(self.base_link, q)

                r = client.request(q)

                r = client.parseDOM(r, 'div', attrs = {'class': 'item'})
                r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'span', attrs = {'class': 'tt'}), client.parseDOM(r, 'span', attrs = {'class': 'year'}))
                r = [(i[0], re.sub('(?:\(|\s)\('+year+'.+', '', i[1]).strip().encode('utf-8'), i[2]) for i in r if len(i[0]) > 0 and '/series/' in i[0] and len(i[1]) > 0 and len(i[2]) > 0]
                r = [i[0] for i in r if year == i[2]][0]

            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'url': r}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            show = data['url'].split('/')[4]
            r = urlparse.urljoin(self.base_link, self.episode_link % (show, season, episode))
            url = re.findall('(?://.+?|)(/.+)', r)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            pass

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            r = urlparse.urljoin(self.base_link, url)

            result = client.request(r)

            f = client.parseDOM(result, 'div', attrs = {'class': 'movieplay'})
            if not f:
                f = client.parseDOM(result, 'div', attrs={'class': 'embed2'})
                f = client.parseDOM(f, 'div')

            f = client.parseDOM(f, 'iframe', ret='data-lazy-src')

            dupes = []

            for u in f:
                try:
                    sid = urlparse.parse_qs(urlparse.urlparse(u).query)['id'][0]

                    if sid in dupes: raise Exception()
                    dupes.append(sid)
                    if 'stream/ol.php' in u:
                        url = client.request(u, timeout='10', XHR=True, referer=u)
                        url = client.parseDOM(url, 'iframe', ret='src')[0]
                        sources.append({'source': 'openload.co', 'quality': 'HD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})

                    if 'stream/play.php' in u:
                        url = client.request(u, timeout='10', XHR=True, referer=u)
                        url = client.parseDOM(url, 'a', ret='href')
                        url = [i for i in url if '.php' in i][0]
                        url = 'http:' + url if url.startswith('//') else url
                        url = client.request(url, timeout='10', XHR=True, referer=u)

                        url = re.findall('sources\s*:\s*\[(.+?)\]', url)[0]
                        links = json.loads('[' + url + ']')

                        for i in links:
                            try:
                                quality = re.findall('(\d+)', i['label'])[0]
                                if int(quality) >= 1080: quality = '1080p'
                                elif 720 <= int(quality) < 1080: quality = 'HD'
                                else: quality = 'SD'

                                try:
                                    quality = directstream.googletag(i['file'])[0]['quality']
                                except:
                                    pass

                                sources.append({'source': 'gvideo', 'quality': quality, 'language': 'en', 'url': i['file'], 'direct': True, 'debridonly': False})
                            except:
                                pass
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return directstream.googlepass(url)


