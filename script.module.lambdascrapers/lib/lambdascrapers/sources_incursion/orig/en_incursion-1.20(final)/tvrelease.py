# -*- coding: utf-8 -*-

'''
    Covenant Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''



import re,urlparse, traceback

from urllib import urlencode

from threading import Thread
from bs4 import BeautifulSoup
from resources.lib.modules import debrid, cfscrape, source_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['tv-release.pw', 'tv-release.immunicity.st']
        self.base_link = 'http://tv-release.pw'
        self.search_link = '?s=%s'
        self.scraper = cfscrape.create_scraper()
        self.threads = []
        self.sourceList = []
        self.validHosts = []

    def getPost(self, url):
        soup = BeautifulSoup(self.scraper.get(url).text, 'html.parser')
        title = soup.find('div', {'class':'notifierbar'}).text
        links = soup.find('table', {'id':'download_table'}).findAll('a')
        quality = source_utils.get_quality_simple(title)
        info = source_utils.get_info_simple(title)

        for link in links:
            valid, host = source_utils.checkHost(link['href'], self.validHosts)
            if valid:
                self.sourceList.append(
                    {'source': host, 'quality': quality, 'language': 'en', 'url': link['href'], 'info': info, 'direct': False,
                     'debridonly': True})

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            return url
        except:
            traceback.print_exc()
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            return url
        except:
            traceback.print_exc()
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            print("INFO - " + str(url))
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            return url
        except:
            traceback.print_exc()
            return


    def sources(self, url, hostDict, hostprDict):

        try:
            self.validHosts = hostprDict + hostDict

            sources = []

            if url == None: return sources
            print('URL INFO - ' + str(url))

            if not debrid.status(): raise Exception()

            if 'tvshowtitle' in url:
                url['season'] = '%02d' % int(url['season'])
                url['episode'] = '%02d' % int(url['episode'])
                query = '%s S%sE%s' % (url['tvshowtitle'], url['season'], url['episode'])
            else:
                query = '%s %s' % (url['title'], url['year'])

                query = urlencode(query)

            url = self.search_link % query
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url)

            r = BeautifulSoup(r.text, 'html.parser')
            posts = r.findAll('h2')
            for post in posts:
                if query.lower() in post.text.lower():
                    postLink = post.find('a')['href']
                    self.threads.append(Thread(target=self.getPost, args=(postLink,)))

            for i in self.threads:
                i.start()
            for i in self.threads:
                i.join()

            return self.sourceList
        except:
            traceback.print_exc()

    def resolve(self, url):
        return url
