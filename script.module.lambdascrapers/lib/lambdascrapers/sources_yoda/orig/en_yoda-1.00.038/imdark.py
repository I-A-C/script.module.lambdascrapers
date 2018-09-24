# -*- coding: utf-8 -*-

'''
    Yoda Add-on
    Copyright (C) 2015 lambda

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


import re,urllib,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['imdark.com']
        self.base_link = 'http://imdark.com'
        self.search_link = '/?s=%s&lang=en'
        self.ajax_link = '/wp-admin/admin-ajax.php'
       

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return None

  

    def sources(self, url, hostDict, locDict):
        sources = []

        try:
            if url == None: return sources
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)
            #query = urlparse.urljoin(self.base_link, self.ajax_link)            
            #post = urllib.urlencode({'action':'sufi_search', 'search_string': title})
            
            result = client.request(query)
            r = client.parseDOM(result, 'div', attrs={'id':'showList'})
            r = re.findall(r'<a\s+style="color:white;"\s+href="([^"]+)">([^<]+)', r[0])     
            r = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1]) and data['year'] in i[1]][0]
            url = r[0]                     
            result = client.request(url)
            r = re.findall(r'video\s+id="\w+.*?src="([^"]+)".*?data-res="([^"]+)',result,re.DOTALL)
            
            for i in r:                
                try:
                    q = source_utils.label_to_quality(i[1])
                    sources.append({'source': 'CDN', 'quality': q, 'language': 'en', 'url': i[0], 'direct': True, 'debridonly': False})                
                except:
                    pass

            return sources
        except Exception as e:
            return sources

    def resolve(self, url):
        return url
