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

import re, traceback, urlparse, urllib, base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cinemamega.net']
        self.base_link = 'http://cinemamega.net'
        self.search_link = '/search-movies/%s.html'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))

            results = client.request(search_url)
            results = client.parseDOM(results, 'div', {'id': 'movie-featured'})
            results = [(client.parseDOM(i, 'a', ret='href'),
                  re.findall('.+?elease:\s*(\d{4})</', i),
                  re.findall('<b><i>(.+?)</i>', i)) for i in results]
            results = [(i[0][0], i[1][0], i[2][0]) for i in results if
                 (cleantitle.get(i[2][0]) == cleantitle.get(title) and i[1][0] == year)]
            url = results[0][0]

            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('CinemaMega - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('CinemaMega - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['premiered'], url['season'], url['episode'] = premiered, season, episode
            try:
                clean_title = cleantitle.geturl(url['tvshowtitle'])+'-season-%d' % int(season)
                search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
                search_results = client.request(search_url)
                parsed = client.parseDOM(search_results, 'div', {'id': 'movie-featured'})
                parsed = [(client.parseDOM(i, 'a', ret='href'), re.findall('<b><i>(.+?)</i>', i)) for i in parsed]
                parsed = [(i[0][0], i[1][0]) for i in parsed if cleantitle.get(i[1][0]) == cleantitle.get(clean_title)]
                url = parsed[0][0]
            except:
                pass
            data = client.request(url)
            data = client.parseDOM(data, 'div', attrs={'id': 'details'})
            data = zip(client.parseDOM(data, 'a'), client.parseDOM(data, 'a', ret='href'))
            url = [(i[0], i[1]) for i in data if i[0] == str(int(episode))]

            return url[0][0]
        except:
            failure = traceback.format_exc()
            log_utils.log('CinemaMega - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            html = client.request(url)
            try:
                v = re.findall('document.write\(Base64.decode\("(.+?)"\)', html)[0]
                b64 = base64.b64decode(v)
                url = client.parseDOM(b64, 'iframe', ret='src')[0]
                try:
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': url.replace('\/', '/'), 'direct': False, 'debridonly': False})
                except:
                    pass
            except:
                pass
            parsed = client.parseDOM(html, 'div', {'class': 'server_line'})
            parsed = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'p', attrs={'class': 'server_servername'})[0]) for i in parsed]
            if parsed:
                for i in parsed:
                    try:
                        host = re.sub('Server|Link\s*\d+', '', i[1]).lower()
                        url = i[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        if 'other'in host: continue
                        sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': url.replace('\/', '/'), 'direct': False, 'debridonly': False})
                    except:
                        pass
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('CinemaMega - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        if self.base_link in url:
            url = client.request(url)
            v = re.findall('document.write\(Base64.decode\("(.+?)"\)', url)[0]
            b64 = base64.b64decode(v)
            url = client.parseDOM(b64, 'iframe', ret='src')[0]
        return url
