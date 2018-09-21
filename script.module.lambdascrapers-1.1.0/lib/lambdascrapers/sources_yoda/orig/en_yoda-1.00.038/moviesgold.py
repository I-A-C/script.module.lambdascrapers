'''
    Yoda Add-on
    Copyright (C) 2016 Yoda

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
import re
import urllib
import urlparse
import json

from resources.lib.modules import client, cleantitle, directstream

class source:
    def __init__(self):
        '''
        Constructor defines instances variables

        '''
        self.priority = 1
        self.language = ['en']
        self.domains = ['moviesgolds.net']
        self.base_link = 'http://www.moviesgolds.net'
        self.search_path = ('?s=%s')

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            query = ('%s-%s' % (clean_title, year))
            url = urlparse.urljoin(self.base_link, query)
            response = client.request(url)

            url = re.findall('''<a\s*href=['\"](http://www\.buzzmovie\.site/\?p=\d+)''', response)[0]

            return url
        except Exception:
            return
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
                    
            info_response = client.request(url)

            iframes = re.findall('''<iframe\s*src=['"]([^'"]+)''', info_response)

            for url in iframes:
                host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                if host in hostDict:
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': 'en',
                        'url': url.replace('\/','/'),
                        'direct': False,
                        'debridonly': False
                    })
            return sources
        except Exception:
            return

    def resolve(self, url):
        return url
