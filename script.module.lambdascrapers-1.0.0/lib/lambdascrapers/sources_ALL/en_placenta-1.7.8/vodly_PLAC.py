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

import re,traceback,urlparse,urllib,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import dom_parser2
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vodly.us', 'vodly.unblocked.tv', 'watch32.is']
        self.base_link = 'http://watch32.is'
        self.search_link = '/%s/search?q=watch32.is+%s+%s'
        self.goog = 'https://www.google.co.uk'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            scrape = title.lower().replace(' ','+').replace(':', '')

            start_url = self.search_link %(self.goog,scrape,year)

            html = client.request(start_url)
            results = re.compile('href="(.+?)"',re.DOTALL).findall(html)
            for url in results:
                if self.base_link in url:
                    if 'webcache' in url:
                        continue
                    if cleantitle.get(title) in cleantitle.get(url):
                        chkhtml = client.request(url)
                        chktitle = re.compile('<title>(.+?)</title>',re.DOTALL).findall(chkhtml)[0]
                        if cleantitle.get(title) in cleantitle.get(chktitle):
                            if year in chktitle:
                                return url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('Vodly - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            if url is None: return sources
            sources = []

            result = client.request(url)
            res_chk = re.compile('<title>(.+?)</title>',re.DOTALL).findall(result)[0]
            r = client.parseDOM(result, 'tbody')
            r = client.parseDOM(r, 'tr')
            r = [(re.findall('<td>(.+?)</td>', i)[0], client.parseDOM(i, 'a', ret='href')[0]) for i in r]

            if r:
                for i in r:
                    try:
                        hostchk = i[0]
                        if 'other'in hostchk: continue

                        vid_page = urlparse.urljoin(self.base_link, i[1])
                        html = client.request(vid_page)
                        vid_div = re.compile('<div class="wrap">(.+?)</div>',re.DOTALL).findall(html)[0]
                        vid_url = re.compile('href="(.+?)"',re.DOTALL).findall(vid_div)[0]
                        quality,info = source_utils.get_release_quality(res_chk, vid_url)
                        host = vid_url.split('//')[1].replace('www.','')
                        host = host.split('/')[0].lower()
                        sources.append({
                            'source': host,
                            'quality': quality,
                            'language': 'en',
                            'url':vid_url,
                            'info':info,
                            'direct': False,
                            'debridonly': False
                        })
                    except:
                        pass
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('Vodly - Exception: \n' + str(failure))
            return

    def resolve(self, url):
        if self.base_link in url:
            url = client.request(url)
            url = client.parseDOM(url, 'div', attrs={'class': 'wrap'})
            url = client.parseDOM(url, 'a', ret='href')[0]
        return url