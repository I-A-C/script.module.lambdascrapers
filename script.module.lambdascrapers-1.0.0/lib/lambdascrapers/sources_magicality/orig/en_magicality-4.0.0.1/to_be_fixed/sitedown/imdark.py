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

import re,traceback,urllib,urlparse,requests

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import directstream

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['imdark.com']
        self.base_link = 'http://imdark.com/'
        self.search_link = '/?s=%s&darkestsearch=%s'
        self.ajax_link = '/wp-admin/admin-ajax.php'
       

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            traceback.print_exc()
            return None


    def sources(self, url, hostDict, locDict):
        sources = []
        req = requests.Session()
        headers = {'User-Agent': client.randomagent(), 'Origin': 'http://imdark.com', 'Referer': 'http://imdark.com',
                   'X-Requested-With': 'XMLHttpRequest'}

        try:
            if url == None: return sources
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            query = urllib.quote_plus(title).lower()
            result = req.get(self.base_link, headers=headers).text
            darksearch = re.findall(r'darkestsearch" value="(.*?)"', result)[0]

            result = req.get(self.base_link + self.search_link % (query, darksearch), headers=headers).text

            r = client.parseDOM(result, 'div', attrs={'id':'showList'})
            r = re.findall(r'<a\s+style="color:white;"\s+href="([^"]+)">([^<]+)', r[0])     
            r = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1]) and data['year'] in i[1]][0]
            url = r[0]
            print("INFO - " + url)
            result = req.get(url, headers=headers).text
            nonce = re.findall(r"nonce = '(.*?)'", result)[0]
            tipi = re.findall(r'tipi = (.*?);', result)[0]
            postData = {'action':'getitsufiplaying', 'tipi':tipi, 'jhinga':nonce}
            result = req.post(self.base_link + self.ajax_link, data=postData, headers=headers).text
            r = re.findall(r'"src":"(.*?)","type":"(.*?)","data-res":"(\d*?)"', result)
            linkHeaders = 'Referer=http://imdark.com/&User-Agent=' + urllib.quote(client.randomagent()) + '&Cookie=' + urllib.quote('mykey123=mykeyvalue')
            for i in r:
                print(str(i))
                try:
                    q = source_utils.label_to_quality(i[2])
                    sources.append({'source': 'CDN', 'quality': q, 'info': i[1].replace('\\', ''), 'language': 'en',
                                    'url': i[0].replace('\\','') + '|' + linkHeaders,
                                    'direct': True, 'debridonly': False})
                except:
                    traceback.print_exc()
                    pass
            for i in sources:
                print("INFO SOURCES " + str(i))
            return sources
        except:
            traceback.print_exc()
            return sources

    def resolve(self, url):
        return url
