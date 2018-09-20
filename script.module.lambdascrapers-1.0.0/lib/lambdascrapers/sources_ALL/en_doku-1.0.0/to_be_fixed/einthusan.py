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


import re,urllib,urllib2,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['einthusan.com', 'einthusan.tv']
        self.base_link = 'https://einthusan.tv'
        self.search_link = '/movie/results/?lang=%s&query=%s'
        self.movie_link = '/movie/watch/%s/'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            langMap = {'hi':'hindi', 'ta':'tamil', 'te':'telugu', 'ml':'malayalam', 'kn':'kannada', 'bn':'bengali', 'mr':'marathi', 'pa':'punjabi'}

            lang = 'http://www.imdb.com/title/%s/' % imdb
            lang = client.request(lang)
            lang = re.findall('href\s*=\s*[\'|\"](.+?)[\'|\"]', lang)
            lang = [i for i in lang if 'primary_language' in i]
            lang = [urlparse.parse_qs(urlparse.urlparse(i).query) for i in lang]
            lang = [i['primary_language'] for i in lang if 'primary_language' in i]
            lang = langMap[lang[0][0]]

            q = self.search_link % (lang, urllib.quote_plus(title))
            q = urlparse.urljoin(self.base_link, q)

            t = cleantitle.get(title)

            r = client.request(q)

            r = client.parseDOM(r, 'li')
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'h3'), client.parseDOM(i, 'div', attrs = {'class': 'info'})) for i in r]
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if i[0] and i[1] and i[2]]
            r = [(re.findall('(\d+)', i[0]), i[1], re.findall('(\d{4})', i[2])) for i in r]
            r = [(i[0][0], i[1], i[2][0]) for i in r if i[0] and i[2]]
            r = [i[0] for i in r if t == cleantitle.get(i[1]) and year == i[2]][0]

            url = str(r)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = self.movie_link % url
            url = urlparse.urljoin(self.base_link, url)

            return sources

            r = client.request(url)

            sources.append({'source': 'einthusan', 'quality': 'HD', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


