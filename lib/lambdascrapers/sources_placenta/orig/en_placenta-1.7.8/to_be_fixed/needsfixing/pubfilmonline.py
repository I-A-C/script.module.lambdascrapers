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


import re,traceback,urllib,urlparse,json,requests

from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['pubfilmonline.net']
        self.base_link = 'http://pubfilmonline.net/'
        self.ajax_link = '/?s=%s'
        self.search_link = '/wp-admin/admin-ajax.php'
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
