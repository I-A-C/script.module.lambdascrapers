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


import re,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import jsunpack


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movieocean.net']
        self.base_link = 'http://movieocean.net'
        self.search_link = 'aHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vY3VzdG9tc2VhcmNoL3YxZWxlbWVudD9rZXk9QUl6YVN5Q1ZBWGlVelJZc01MMVB2NlJ3U0cxZ3VubU1pa1R6UXFZJnJzej1maWx0ZXJlZF9jc2UmbnVtPTEwJmhsPWVuJmN4PTAwNjkxOTYxOTI2MzYxNzgyMDM4ODpkYmljLTZweGt4cyZnb29nbGVob3N0PXd3dy5nb29nbGUuY29tJnE9JXM='
        self.moviesearch_link = '/watch/%s-%s'
        self.tvsearch_link = '/watch/%s-%s-season-%s/%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = cleantitle.get(title)

            q = '%s %s' % (title, year)
            q = self.search_link.decode('base64') % urllib.quote_plus(q)

            r = client.request(q)
            r = json.loads(r)['results']
            r = [(i['url'], i['titleNoFormatting']) for i in r]
            r = [(i[0].split('%')[0], re.findall('(?:^Watch |)(.+?)(?:\(|)(\d{4})', i[1])) for i in r]
            r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if i[1]]
            r = [i for i in r if '/watch/' in i[0] and not '-season-' in i[0]]
            r = [i for i in r if t == cleantitle.get(i[1]) and year == i[2]]
            r = r[0][0]

            url = re.findall('(?://.+?|)(/.+)', r)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            pass

        try:
            url = re.sub('[^A-Za-z0-9]', '-', title).lower()
            url = self.moviesearch_link % (url, year)

            r = urlparse.urljoin(self.base_link, url)
            r = client.request(r, output='geturl')
            if not year in r: raise Exception()

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

            year = re.findall('(\d{4})', premiered)[0]
            if int(year) >= 2016: raise Exception()

            url = re.sub('[^A-Za-z0-9]', '-', data['tvshowtitle']).lower()
            url = self.tvsearch_link % (url, data['year'], '%01d' % int(season), '%01d' % int(episode))

            r = urlparse.urljoin(self.base_link, url)
            r = client.request(r, output='geturl')
            if not data['year'] in r: raise Exception()

            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)
            r = client.parseDOM(r, 'div', attrs = {'class': 'player_wraper'})
            r = client.parseDOM(r, 'iframe', ret='src')[0]
            r = urlparse.urljoin(url, r)
            r = client.request(r, referer=url)
            a = client.parseDOM(r, 'div', ret='value', attrs = {'id': 'k2'})[-1]
            b = client.parseDOM(r, 'div', ret='value', attrs = {'id': 'k1'})[-1]
            c = client.parseDOM(r, 'body', ret='style')[0]
            c = re.findall('(\d+)',  c)[-1]
            r = '/player/%s?s=%s&e=%s' % (a, b, c)
            r = urlparse.urljoin(url, r)
            r = client.request(r, referer=url)
            r = re.findall('"(?:url|src)"\s*:\s*"(.+?)"', r)

            for i in r:
                try: sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                except: pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return directstream.googlepass(url)


