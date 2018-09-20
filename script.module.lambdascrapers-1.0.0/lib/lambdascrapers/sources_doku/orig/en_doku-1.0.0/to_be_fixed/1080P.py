'''
    Incursion Add-on
    Copyright (C) 2016 Incursion

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


import re,urllib,urlparse,json,base64

from ptw.libraries import cleantitle
from ptw.libraries import client
from ptw.libraries import directstream
from ptw.libraries import source_utils
from resources.lib.libraries import cfscrape
from ptw.libraries import dom_parser2

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['1080pmovie.com','watchhdmovie.net']
        self.base_link = 'https://watchhdmovie.net'
        self.search_link = '%s/%s-watch/'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None: return
            urldata = urlparse.parse_qs(url)
            urldata = dict((i, urldata[i][0]) for i in urldata)
            clean_title = cleantitle.geturl(urldata['title'])
            start_url = self.search_link % (self.base_link, clean_title)
            data = self.scraper.get(start_url).content
            r = dom_parser2.parse_dom(data, 'button', {'id': 'iframelink'})
            links = [i.attrs['value'] for i in r]
            for i in links:
                try:
                    valid, host = source_utils.is_host_valid(i, hostDict)
                    if not valid: continue
                    sources.append({'source':host,'quality':'1080p','language': 'en','url':i,'info':[],'direct':False,'debridonly':False})
                except:
                    pass
            return sources
        except:
            return sources



    def resolve(self, url):
        return url
