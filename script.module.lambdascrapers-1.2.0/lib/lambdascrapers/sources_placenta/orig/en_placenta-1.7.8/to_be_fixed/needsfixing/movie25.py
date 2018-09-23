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

import re,urllib,urlparse,json,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['movie25.ph', 'movie25.hk', 'tinklepad.is', 'tinklepad.ag', 'movie25.ag','5movies.to','movie25.unblocked.tv']
        self.base_link = 'http://5movies.to'
        self.search_link = '/search.php?q=%s'
        self.search_link_2 = 'https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=10&hl=en&cx=008492768096183390003:0ugusjabnlq&googlehost=www.google.com&q=%s'
        self.video_link = '/getlink.php?Action=get&lk=%s'

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

    def _search(self, title, year, aliases, headers):
        try:
            q = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(title)))
            r = client.request(q)
            r = client.parseDOM(r, 'div', attrs={'class':'ml-img'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'img', ret='alt'))
            url = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1]) and year in i[1]][0][0]

            return url
        except:
            pass

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            year = data['year']

            if 'tvshowtitle' in data:    
                episode = data['episode']
                season = data['season']
                url = self._search(data['tvshowtitle'], data['year'], aliases, headers)
                url = url.replace('online-free','season-%s-episode-%s-online-free'%(season,episode))

            else:
                episode = None
                year = data['year']
                url = self._search(data['title'], data['year'], aliases, headers)

            
            url = url if 'http' in url else urlparse.urljoin(self.base_link, url)
            result = client.request(url);

            result = client.parseDOM(result, 'li', attrs={'class':'link-button'})
            links = client.parseDOM(result, 'a', ret='href')
            i = 0
            for l in links:
                if i == 10: break
                try:
                    l = l.split('=')[1]
                    l = urlparse.urljoin(self.base_link, self.video_link%l)
                    result = client.request(l, post={}, headers={'Referer':url})
                    u = result if 'http' in result else 'http:'+result 
                    if 'google' in u:
                        valid, hoster = source_utils.is_host_valid(u, hostDict)
                        urls, host, direct = source_utils.check_directstreams(u, hoster)
                        for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
             
                    else:
                        valid, hoster = source_utils.is_host_valid(u, hostDict)
                        if not valid: continue
                        try:
                            u.decode('utf-8')
                            sources.append({'source': hoster, 'quality': 'SD', 'language': 'en', 'url': u, 'direct': False, 'debridonly': False})
                            i+=1
                        except:
                            pass
                    
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
