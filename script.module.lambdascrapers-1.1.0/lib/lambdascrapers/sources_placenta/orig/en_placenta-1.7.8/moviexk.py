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


import re,urllib,urlparse,json, base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import cache


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['moviexk.com', 'moviexk.co']
        self.base_link = 'http://moviexk.co/'
        self.search_link = '/search/%s'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

    def searchMovie(self, title, year, aliases):
        try:
            url = '%s/%s-%s/' % (self.base_link, cleantitle.geturl(title), year)
            url = client.request(url, output='geturl')

            if url == None:
                t = cleantitle.get(title)
                q = '%s %s' % (title, year)
                q = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(q))
                r = client.request(q)
                r = client.parseDOM(r, 'div', attrs={'class': 'inner'})
                r = client.parseDOM(r, 'div', attrs={'class': 'info'})
                r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
                r = [(i[0], re.findall('(?:^Watch Movie |^Watch movies |^Watch |)(.+?)\((\d{4})', i[1])) for i in r]
                r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if i[1]]
                url = [i[0] for i in r if self.matchAlias(i[1], aliases) and year == i[2]][0]

            if url == None: raise Exception()
            return url
        except:
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = self.searchMovie(title, year, aliases)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            q = '%s' % tvshowtitle
            q = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(q))

            r = client.request(q)

            r = client.parseDOM(r, 'div', attrs={'class': 'inner'})
            r = client.parseDOM(r, 'div', attrs={'class': 'info'})
            r = zip(client.parseDOM(r, 'a', ret='href'),client.parseDOM(r, 'a', ret='title'))
   
            r = [(i[0], re.findall('(?:^Watch Movie |^Watch movies |^Watch |)(.+?)\((.+?)', i[1])) for i in r]
            r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if i[1]]
            r = [(i[0], i[1].rsplit('TV Series')[0].strip('(')) for i in r if i[1]]
            r = [(urllib.unquote_plus(i[0]), i[1]) for i in r]
            r = [(urlparse.urlparse(i[0]).path, i[1]) for i in r]
            r = [i for i in r if self.matchAlias(i[1], aliases)]

            r = urlparse.urljoin(self.base_link, r[0][0].strip())

            if '/watch-movie-' in r: r = re.sub('/watch-movie-|-\d+$', '/', r)

            y = re.findall('(\d{4})', r)

            if y:
                y = y[0]
            else:
                y = client.request(r)
                y = re.findall('(?:D|d)ate\s*:\s*(\d{4})', y)[0]

            if not year == y: raise Exception()

            url = re.findall('(?://.+?|)(/.+)', r)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = '%s?season=%01d&episode=%01d' % (url, int(season), int(episode))
            return url 
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            f = urlparse.urljoin(self.base_link, url)

            url = f.rsplit('?', 1)[0]

            r = client.request(url, mobile=True)

            p = client.parseDOM(r, 'div', attrs = {'id': 'servers'})

            if not p:
                p = client.parseDOM(r, 'div', attrs = {'class': 'btn-groups.+?'})
                p = client.parseDOM(p, 'a', ret='href')[0]

                p = client.request(p, mobile=True)
                p = client.parseDOM(p, 'div', attrs = {'id': 'servers'})

            r = client.parseDOM(p, 'li')
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))

            try:
                s = urlparse.parse_qs(urlparse.urlparse(f).query)['season'][0]
                e = urlparse.parse_qs(urlparse.urlparse(f).query)['episode'][0]
                r = [(i[0], re.findall('(\d+)', i[1])) for i in r]
                r = [(i[0], '%01d' % int(i[1][0]), '%01d' % int(i[1][1])) for i in r if len(i[1]) > 1]
                r = [i[0] for i in r if s == i[1] and e == i[2]]
            except:
                r = [i[0] for i in r]

            for u in r:
                try:
                    headers = {'Referer': u}
                    url = client.request(u, headers=headers)
                    url = client.parseDOM(url, 'source', ret='src')
                    for i in url:
                        rd = client.request(i, headers=headers, output='geturl')
                        if '.google' in rd:
                            sources.append({'source': 'gvideo', 'quality': directstream.googletag(rd)[0]['quality'], 'language': 'en', 'url': rd, 'direct': True, 'debridonly': False})
                except:
                    pass

                try:
                    url = client.request(u, mobile=True)
                    url = client.parseDOM(url, 'source', ret='src')
                    if '../moviexk.php' in url[0]:
                        url[0] = url[0].replace('..','')
                        url[0] = urlparse.urljoin(self.base_link, url[0])
                        url[0] = client.request(url[0], mobile=True, output='geturl')
                    else:
                        url = [i.strip().split()[0] for i in url]

                    for i in url:
                        try:
                            sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                        except:
                            pass
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return directstream.googlepass(url)


