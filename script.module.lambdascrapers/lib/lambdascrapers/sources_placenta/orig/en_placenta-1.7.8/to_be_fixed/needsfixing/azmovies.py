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

import re, requests, base64, urllib, urlparse
import resolveurl as urlresolver

from resources.lib.modules import cleantitle
from resources.lib.modules import client

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['azmovies.ws', 'azmovies.xyz']
        self.base_link = 'https://azmovies.xyz/'
        self.search_link = '/search.php?q=%s'
        self.scrape_type = 0 #0 = Movies, 1 = TV Shows

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            self.scrape_type = 0

            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url  % (title.replace(':', ' ').replace(' ', '+'))

            search_results = client.request(url)
            match = re.compile('span class="play-btn".+?href="(.+?)".+?class="card-title title">(.+?)</span>',re.DOTALL).findall(search_results)
            for item_url,item_title in match:
                if cleantitle.get(title) in cleantitle.get(item_title):
                    item_url = urlparse.urljoin(self.base_link, item_url)
                    html = client.request(item_url)
                    date = re.compile('Release:(.+?)<br>',re.DOTALL).findall(html)[0]
                    if year in str(date):
                        return item_url
            return
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
            self.scrape_type = 1
            if url == None: return
            urldata = urlparse.parse_qs(url)
            urldata = dict((i, urldata[i][0]) for i in urldata)
            title = urldata['tvshowtitle'].replace(':', ' ').lower()

            search_id = common.clean_search(title.lower())
            search_results = self.search_link % (self.base_link,search_id.replace(' ','+'))
            html = client.request(search_results)
            match = re.compile('span class="play-btn".+?href="(.+?)".+?class="card-title title">(.+?)</span>',re.DOTALL).findall(html)
            for item_url,item_title in Regex:
                show_check = '%s - Season%s' % (search_id,season)
                if not common.clean_title(show_check).lower() == common.clean_title(item_title).lower():
                    continue
                item_url = urlparse.urljoin(self.base_link, item_url)
            return tvshow_link
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        if url == None: return
        try:
            if self.scrape_type == 0:
                html = client.request(url)
                match = re.compile("<ul id='serverul'(.+?)</ul>",re.DOTALL).findall(html)
                Links = re.compile('<a href="(.+?)"',re.DOTALL).findall(str(match))
                for link in Links:
                    if urlresolver.HostedMediaFile(link):
                        if '1080' in link:
                            quality = '1080p'
                        elif '720' in link:
                            quality='720p'
                        else:
                            quality='SD'
                        host = link.split('//')[1].replace('www.','')
                        host = host.split('/')[0].split('.')[0].title()
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})
                return sources
            else:
                season_page = client.request(url)
                episodes = re.compile('target="iframe" href="(.+?)"',re.DOTALL).findall(season_page)
                for link in episodes:
                    if urlresolver.HostedMediaFile(link):
                        if '1080' in link:
                            quality = '1080p'
                        elif '720' in link:
                            quality='720p'
                        else:
                            quality='SD'
                        host = link.split('//')[1].replace('www.','')
                        host = host.split('/')[0].split('.')[0].title()
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})
                return sources
        except:
            return sources

    def resolve(self, url):
        return url