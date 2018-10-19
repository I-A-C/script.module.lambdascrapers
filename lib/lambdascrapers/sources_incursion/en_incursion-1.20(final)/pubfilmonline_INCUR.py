# -*- coding: utf-8 -*-

'''
    Incursion Add-on

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

import re,urllib,json, requests

from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['http://getmypopcornnow.xyz','getmypopcornnow.xyz']
        self.base_link = 'http://pubfilmonline.net'
        self.ajax_link = '/wp-admin/admin-ajax.php'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        searchTitle = cleantitle.geturl(title + "-" + year)
        url = '/movies/%s/' % searchTitle
        req = self.scraper.get(self.base_link + url)
        url = self.ajax_call(req)
        return url

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return tvshowtitle

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            searchTitle = cleantitle.geturl(url)
            url = self.base_link +"/episodes/%s-%sx%s" % (searchTitle, season, episode)
            req = self.scraper.get(url)
            url = self.ajax_call(req)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            for i in url:
                sources.append({'source': 'CDN', 'quality': i['label'], 'language': 'en', 'url': i['file'], 'direct': True,
                                'debridonly': False})
            return sources
        except:
            return

    def ajax_call(self, req):
        video_id = re.findall(r'ajax_get_video_info":"(.*?)"', req.text)[0]
        ids = re.findall(r'data-ids="(.*?)">', req.text)[0]
        post = {'action': 'ajax_get_video_info', 'ids': ids, 'server': '1', 'nonce': video_id}
        req = self.scraper.post(self.base_link + self.ajax_link, data=post)
        try:
            url = json.loads(req.text)
            return url
        except:
            url = None
            return url

    def resolve(self, url):
        return url


#url = source.movie(source(), '', 'The Shape Of Water','','' '','2017')
#url = source.episode(source(),'The Walking Dead','', '', '', '', '8', '6')
#sources = source.sources(source(),url,'',['1fichier.com', 'oboom.com', 'rapidgator.net', 'rg.to', 'uploaded.net', 'uploaded.to', 'ul.to', 'filefactory.com', 'nitroflare.com', 'turbobit.net', 'uploadrocket.net'])
