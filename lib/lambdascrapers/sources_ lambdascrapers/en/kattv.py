# -*- coding: UTF-8 -*-
'''
    kattv scraper for Exodus forks.
    Nov 9 2018 - Checked

    Updated and refactored by someone.
    Originally created by others.
'''
import re, urlparse, urllib, base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import dom_parser2

import requests
def url_ok(url):
    r = requests.head(url)
    if r.status_code == 200 or r.status_code == 301:
        return True
    else: return False

def HostChcker():
    if url_ok("http://kat.tv"):
        useurl = 'http://kat.tv'

    elif url_ok("http://kat.bypassed.bz"):
        useurl = 'http://kat.bypassed.bz'

    else: useurl = 'http://localhost/'
    
    return useurl

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['kat.tv']
        self.base_link = HostChcker()
        self.search_link = '/search-movies/%s.html'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
            r = cache.get(client.request, 1, search_url)
            r = dom_parser2.parse_dom(r, 'li', {'class': 'item'})
            r = [(dom_parser2.parse_dom(i, 'a', attrs={'class': 'title'}),
                  re.findall('status-year">(\d{4})</div', i.content, re.DOTALL)[0]) for i in r if i]
            r = [(i[0][0].attrs['href'], re.findall('(.+?)</b><br', i[0][0].content, re.DOTALL)[0], i[1]) for i in r if i]
            r = [(i[0], i[1], i[2]) for i in r if (cleantitle.get(i[1]) == cleantitle.get(title) and i[2] == year)]
            url = r[0][0]
            return url
        except Exception:
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
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['premiered'], url['season'], url['episode'] = premiered, season, episode
            try:
                clean_title = cleantitle.geturl(url['tvshowtitle'])+'-season-%d' % int(season)
                search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
                r = cache.get(client.request, 1, search_url)
                r = dom_parser2.parse_dom(r, 'li', {'class': 'item'})
                r = [(dom_parser2.parse_dom(i, 'a', attrs={'class': 'title'}),
                      dom_parser2.parse_dom(i, 'div', attrs={'class':'status'})[0]) for i in r if i]
                r = [(i[0][0].attrs['href'], re.findall('(.+?)</b><br', i[0][0].content, re.DOTALL)[0],
                      re.findall('(\d+)', i[1].content)[0]) for i in r if i]
                r = [(i[0], i[1].split(':')[0], i[2]) for i in r
                     if (cleantitle.get(i[1].split(':')[0]) == cleantitle.get(url['tvshowtitle']) and i[2] == str(int(season)))]
                url = r[0][0]
            except:
                pass
            data = client.request(url)
            data = client.parseDOM(data, 'div', attrs={'id': 'details'})
            data = zip(client.parseDOM(data, 'a'), client.parseDOM(data, 'a', ret='href'))
            url = [(i[0], i[1]) for i in data if i[0] == str(int(episode))]

            return url[0][1]
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = cache.get(client.request, 1, url)
            try:
                v = re.findall('document.write\(Base64.decode\("(.+?)"\)', r)[0]
                b64 = base64.b64decode(v)
                url = client.parseDOM(b64, 'iframe', ret='src')[0]
                try:
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': 'en',
                        'url': url.replace('\/', '/'),
                        'direct': False,
                        'debridonly': False
                    })
                except:
                    pass
            except:
                pass
            r = client.parseDOM(r, 'div', {'class': 'server_line'})
            r = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'p', attrs={'class': 'server_servername'})[0]) for i in r]
            if r:
                for i in r:
                    try:
                        host = re.sub('Server|Link\s*\d+', '', i[1]).lower()
                        url = i[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        if 'other'in host: continue
                        sources.append({
                            'source': host,
                            'quality': 'SD',
                            'language': 'en',
                            'url': url.replace('\/', '/'),
                            'direct': False,
                            'debridonly': False
                        })
                    except:
                        pass
            return sources
        except Exception:
            return

    def resolve(self, url):
        if self.base_link in url:
            try:
                r = client.request(url)
                v = re.findall('document.write\(Base64.decode\("(.+?)"\)', r)[0]
                b64 = base64.b64decode(v)
                url = client.parseDOM(b64, 'iframe', ret='src')[0]
            except:
                r = client.request(url)
                r = client.parseDOM(r, 'div', attrs={'class':'player'})
                url = client.parseDOM(r, 'a', ret='href')[0]

        return url
