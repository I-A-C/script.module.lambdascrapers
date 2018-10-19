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

import urllib, urlparse, re

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser
from resources.lib.modules import directstream
from resources.lib.modules import debrid



class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movie4k.is']
        self.base_link = 'http://movie4k.is'
        self.search_link = '/search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
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

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s' % (data['title'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            posts = client.parseDOM(r, 'item')

            items = []

            for post in posts:

                try:
                    t = client.parseDOM(post, 'title')[0]
                    t2 = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', t)

                    if not cleantitle.get_simple(t2.replace('Watch Online','')) == cleantitle.get(title): raise Exception()

                    l = client.parseDOM(post, 'link')[0]
 
                    p = client.parseDOM(post, 'pubDate')[0]

                    if data['year'] in p: items += [(t, l)]

                except:
                    pass

            print items
            for item in items:
                try:
                    name = item[0]
                    name = client.replaceHTMLCodes(name)
                    
                    u = client.request(item[1])
                    if 'http://www.imdb.com/title/%s/' % data['imdb'] in u:
                        
                        l = client.parseDOM(u, 'div', {'class': 'movieplay'})[0]
                        l = client.parseDOM(u, 'iframe', ret='data-lazy-src')[0]

                        quality, info = source_utils.get_release_quality(name, l)
                        info = ' | '.join(info)

                        url = l

                        url = client.replaceHTMLCodes(url)
                        url = url.encode('utf-8')

                        valid, host = source_utils.is_host_valid(url,hostDict)
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': info, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url
