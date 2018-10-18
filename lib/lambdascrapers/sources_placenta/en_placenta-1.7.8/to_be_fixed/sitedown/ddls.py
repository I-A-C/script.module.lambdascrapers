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
from resources.lib.modules import source_utils
from resources.lib.modules import debrid
from resources.lib.modules import dom_parser2


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['ddlseries.net', 'ddlseries.pw']
        self.base_link = 'http://www.ddlseries.pw'
        self.search_link = '/?q=%s'
        self.search_link2 = '/engine/ajax/search.php'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return		

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

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

            if url is None: return sources

            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            t = data['tvshowtitle']
            season = '%01d' % int(data['season'])
            episode = '%02d' % int(data['episode'])

            query = cleantitle.getsearch(t)
            r = urlparse.urljoin(self.base_link, self.search_link2)
            post = {'query': query}
            r = client.request(r, post=post)
            r = dom_parser2.parse_dom(r, 'a')
            r = [(i.attrs['href'], dom_parser2.parse_dom(i.content, 'span', attrs={'class': 'searchheading'})) for i in
                 r]
            try:
                url = []
                for i in r:
                    t1 = i[1][0].content
                    t2 = re.sub('[Ss]eason\s*\d+', '', t1)
                    if not str(int(season)) in t1: continue
                    if cleantitle.get(t) == cleantitle.get(t2) and not 'pack' in i[0]:
                        url.append(i[0])
                    if len(url) > 1:
                        url = [(i) for i in url if 'hd' in i][0]
                    else:
                        url = url[0]

            except:
                pass
            if len(url) < 0:
                try:
                    r = urlparse.urljoin(self.base_link, self.search_link)
                    t = '%s season %s' % (t, season)
                    post = 'do=search&subaction=search&story=%s' % urllib.quote_plus(cleantitle.getsearch(t))
                    r = client.request(r, post=post)
                    r = dom_parser2.parse_dom(r, 'h4')
                    r = [dom_parser2.parse_dom(i.content, 'a', req=['href']) for i in r if i]
                    r = [(i[0].attrs['href'], i[0].content) for i in r if i]
                    r = [(i[0], i[1]) for i in r if t.lower() == i[1].replace(' -', '').lower()]
                    r = [(i[0]) for i in r if not 'pack' in i[0]]
                    url = r[0][0]

                except:
                    pass

            links = []

            r = client.request(url)
            name = re.findall('<b>Release Name :.+?">(.+?)</span>', r, re.DOTALL)[0]
            link = client.parseDOM(r, 'span', attrs={'class': 'downloads nobr'})
            link = [(re.findall('<a href="(.+?)"\s*target="_blank">[Ee]pisode\s*(\d+)</a>', i, re.DOTALL)) for i in link]
            for item in link:
                link = [(i[0], i[1]) for i in item if i[1] == str(episode)]
                links.append(link[0][0])

            quality, info = source_utils.get_release_quality(name, None)

            for url in links:
                try:
                    if "protect" in url:
                        redirect = client.request(url)
                        url = re.findall('<a href="(.*?)" target="_blank">', redirect)
                        url = url[0]

                    valid, host = source_utils.is_host_valid(url, hostDict)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


