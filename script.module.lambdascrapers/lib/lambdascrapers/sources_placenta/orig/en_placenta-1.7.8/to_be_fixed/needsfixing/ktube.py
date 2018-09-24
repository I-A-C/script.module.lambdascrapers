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

import re,urllib,urlparse,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['kakitube.se']
        self.base_link = 'http://kakitube.se/'
        self.search_link = '/search/%s/feed/rss2/'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
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
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s' % data['tvshowtitle'] if 'tvshowtitle' in data else '%s' % data['title']
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            posts = client.parseDOM(r, 'item')

            for item in posts:
                try:
                    name = client.parseDOM(item, 'title')[0]
                    name = client.replaceHTMLCodes(name)
                    url = client.parseDOM(item, 'link')[0]

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name)

                    if not cleantitle.get(t) == cleantitle.get(title): continue

                    r = client.request(url)
                    if 'tvshows' in url:
                        sep = '%d - %d' % (int(data['season']), int(data['episode']))
                        r = client.parseDOM(r, 'ul', attrs={'class':'episodios'})
                        r = client.parseDOM(r, 'li')
                        r = [(client.parseDOM(i, 'div', attrs={'class':'numerando'})[0],
                              client.parseDOM(i, 'a', ret='href')[0]) for i in r if i]
                        r = [(i[0], i[1]) for i in r if sep in i[0]]
                        link = r[0][1]
                        r = client.request(link)
                        url = client.parseDOM(r, 'iframe', ret='src')[0]
                        url = base64.b64decode(url.split('=',1)[1])

                    else:
                        y = client.parseDOM(r, 'span', attrs={'class':'date'})[0]
                        y = re.findall('(\d{4})', y)[0]
                        if not y == hdlr: continue
                        url = client.parseDOM(r, 'iframe', ret='src')[0]
                        url = base64.b64decode(url.split('=',1)[1])

                    quality, info = source_utils.get_release_quality(name, url)

                    info = ' | '.join(info)

                    if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False})
                except:
                    pass

            check = [i for i in sources if not i['quality'] == 'CAM']
            if check: sources = check

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


