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
from resources.lib.modules import cfscrape



class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['mehlizmovies.com']
        self.base_link = 'https://www.mehlizmovies.com/'
        self.search_link = '?s=%s'
        self.search_link2 = '/search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(
                aliases),year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search(
                [tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = urlparse.urljoin(self.base_link, url)
            scraper = cfscrape.create_scraper()
            data = scraper.get(url).content
            data = client.parseDOM(data, 'ul', attrs={'class': 'episodios'})
            links  = client.parseDOM(data, 'div', attrs={'class': 'episodiotitle'})
            sp = zip(client.parseDOM(data, 'div', attrs={'class': 'numerando'}), client.parseDOM(links, 'a', ret='href'))

            Sea_Epi = '%dx%d'% (int(season), int(episode))
            for i in sp:
                sep = i[0]
                if sep == Sea_Epi:
                    url = source_utils.strip_domain(i[1])

            return url
        except:
            return

    def __search(self, titles, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.getsearch(titles[0])))

            query = urlparse.urljoin(self.base_link, query)

            t = cleantitle.get(titles[0])
            scraper = cfscrape.create_scraper()
            data = scraper.get(query).content
            #data = client.request(query, referer=self.base_link)
            data = client.parseDOM(data, 'div', attrs={'class': 'result-item'})
            r = dom_parser.parse_dom(data, 'div', attrs={'class': 'title'})
            r = zip(dom_parser.parse_dom(r, 'a'), dom_parser.parse_dom(data, 'span', attrs={'class': 'year'}))

            url = []
            for i in range(len(r)):
                title = cleantitle.get(r[i][0][1])
                title = re.sub('(\d+p|4k|3d|hd|season\d+)','',title)
                y = r[i][1][1]
                link = r[i][0][0]['href']
                if 'season' in title: continue
                if t == title and y == year:
                    if 'season' in link:
                        url.append(source_utils.strip_domain(link))
                        print url[0]
                        return url[0]
                    else: url.append(source_utils.strip_domain(link))

            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            links = self.links_found(url)

            hostdict = hostDict + hostprDict
            for url in links:
                try:
                    valid, host = source_utils.is_host_valid(url, hostdict)
                    if 'mehliz' in url:
                        host = 'MZ'; direct = True; urls = (self.mz_server(url))

                    elif 'ok.ru' in url:
                        host = 'vk'; direct = True; urls = (directstream.odnoklassniki(url))

                    else:
                        direct = False; urls = [{'quality': 'SD', 'url': url}]

                    for x in urls:
                        sources.append({'source': host, 'quality': x['quality'], 'language': 'en',
                                        'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def links_found(self,urls):
        try:
            scraper = cfscrape.create_scraper()
            links = []
            if type(urls) is list:
                for item in urls:
                    query = urlparse.urljoin(self.base_link, item)
                    r = scraper.get(query).content
                    data = client.parseDOM(r, 'div', attrs={'id': 'playex'})
                    data = client.parseDOM(data, 'div', attrs={'id': 'option-\d+'})
                    links += client.parseDOM(data, 'iframe', ret='src')
                    print links


            else:
                query = urlparse.urljoin(self.base_link, urls)
                r = scraper.get(query).content
                data = client.parseDOM(r, 'div', attrs={'id': 'playex'})
                data = client.parseDOM(data, 'div', attrs={'id': 'option-\d+'})
                links += client.parseDOM(data, 'iframe', ret='src')

            return links
        except:
            return urls

    def mz_server(self,url):
        try:
            scraper = cfscrape.create_scraper()
            urls = []
            data = scraper.get(url).content
            data = re.findall('''file:\s*["']([^"']+)",label:\s*"(\d{3,}p)"''', data, re.DOTALL)
            for url, label in data:
                label = source_utils.label_to_quality(label)
                if label == 'SD': continue
                urls.append({'url': url, 'quality': label})
            return urls
        except:
            return url

    def resolve(self, url):
        return url
