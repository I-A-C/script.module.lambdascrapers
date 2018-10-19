# -*- coding: utf-8 -*-

'''
    Incursion Add-on

    This is a new script added for the Incursion add-on.

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


import requests
from bs4 import BeautifulSoup
import sys


def clean_search_query(url):
    url = url.replace('-','+')
    url = url.replace(' ', '+')
    return url

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domain = 'allrls.pw'
        self.base_link = 'http://allrls.pw'
        self.search_link = 'http://allrls.pw/?s='
        self.headers = {'Referer':'http://allrls.pw/','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = clean_search_query(title)
            url = {'title': title, 'year': year}
            return url

        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = clean_search_query(tvshowtitle)
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return url
            tvshowtitle = url
            if len(episode) == 1:
                episode = "0" + episode
            if len(season) == 1:
                season = "0" + season
            url = {'cleaned_title': url, 'episode': episode, 'season': season}
            return url
        except:
            print("Unexpected error in AllRLS Episode Script:")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def sources(self, url, hostDict, hostprDict):
        hostDict = hostprDict + hostDict
        try:
            sources = []
            if not url:
                return sources
            with requests.Session() as s:
                if 'episode' in url:
                    tvshowtitle = url['cleaned_title']
                    episode = url['episode']
                    season = url['season']
                    url = (self.search_link + "%s+s%se%s" % (tvshowtitle, season, episode)).lower()
                else:
                    title, year = url['title'], url['year']
                    url = self.search_link + "%s+%s&go=Search" % (title, year)
                post = {'fname':'Hello'}
                p = s.post(self.base_link + "/hello.php", data=post)
                p = s.get(url, headers=self.headers)

                soup = BeautifulSoup(p.text, 'html.parser')
                content = soup.find_all('h2', {'class': 'entry-title'})
                if content[0].text == "Nothing Found":
                    return sources
                for i in content:
                    i = i.find('a')
                    p = s.get(i['href'], headers=self.headers)
                    soup = BeautifulSoup(p.text, 'html.parser')
                    links = soup.find_all('a', href=True, target=True)
                    for i in links:
                        quality = ""
                        i = i['href']
                        if any(x in i for x in ['.rar', '.zip', '.iso']): pass
                        if "720p" in i:
                            quality = "720p"
                        elif "1080p" in i:
                            quality = "1080p"
                        else:
                            quality = "SD"
                        if 'uploadrocket' in i:
                            sources.append(
                                {'source': "uploadrocket.net",
                                 'quality': quality,
                                 'language': "en",
                                 'url': i,
                                 'direct': False,
                                 'debridonly': True})

                        if 'openload' in i:
                            sources.append(
                                {'source': "openload.co",
                                 'quality': quality,
                                 'language': "en",
                                 'url': i,
                                 'direct': False,
                                 'debridonly': False})
                        if 'rapidgator' in i:
                            sources.append(
                                {'source': "rapidgator.net",
                                 'quality': quality,
                                 'language': "en",
                                 'url': i,
                                 'direct': False,
                                 'debridonly': True})
                        if 'uploaded' in i:
                            sources.append(
                                {'source': "uploaded.net",
                                 'quality': quality,
                                 'language': "en",
                                 'url': i,
                                 'direct': False,
                                 'debridonly': True})
                        if 'filefactory' in i:
                            sources.append(
                                {'source': "filefactory.com",
                                 'quality': quality,
                                 'language': "en",
                                 'url': i,
                                 'direct': False,
                                 'debridonly': True})

            return sources

        except:
            print("Unexpected error in AllRLS Source Script:")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return sources

    def resolve(self, url):
            return url
