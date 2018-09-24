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

import re,urllib,urlparse,base64,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['onlinedizi.com']
        self.base_link = 'http://onlinedizi.com'
        self.search_link = '/ajax_submit.php'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            tvshowtitle = cleantitle.getsearch(tvshowtitle)
            p = urllib.urlencode({'action': 'ajaxy_sf', 'sf_value': tvshowtitle, 'search': 'false'})
            r = urlparse.urljoin(self.base_link, self.search_link)
            result = client.request(r, post=p, XHR=True)
            if len(json.loads(result)) == 0:
                p = urllib.urlencode({'action': 'ajaxy_sf', 'sf_value': localtvshowtitle, 'search': 'false'})
                result = client.request(r, post=p, XHR=True)
            diziler = json.loads(result)['diziler'][0]['all']
            for i in diziler:
                if cleantitle.get(tvshowtitle) == cleantitle.get(i['post_title']):
                    url = i['post_link']
                    url = url.split('/')[4]
                    url = url.encode('utf-8')
                    return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if url == None: return

        url = '/%s-%01d-sezon-%01d-bolum/' % (url.replace('/', ''), int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            path = urlparse.urlparse(url).path

            result = client.request(url)
            result = re.sub(r'[^\x00-\x7F]+','', result)
            result = client.parseDOM(result, 'li')
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in result]
            result = [i[0] for i in result if len(i[0]) > 0 and path in i[0][0] and len(i[1]) > 0 and 'Altyaz' in i[1][0]][0][0]

            url = urlparse.urljoin(self.base_link, result)

            result = client.request(url)
            result = re.sub(r'[^\x00-\x7F]+','', result)
            result = client.parseDOM(result, 'div', attrs = {'class': 'video-player'})[0]
            result = client.parseDOM(result, 'iframe', ret='wpfc-data-original-src')[-1]

            try:
                url = base64.b64decode(urlparse.parse_qs(urlparse.urlparse(result).query)['id'][0])
                if not url.startswith('http'): raise Exception()
            except:
                url = client.request(result)
                url = urllib.unquote_plus(url.decode('string-escape'))
                frame = client.parseDOM(url, 'iframe', ret='src')
                if not frame[-1].startswith('http'):
                    frame = 'http:'+frame[-1]
                else:
                    frame = frame[-1]
                if len(frame) > 0:
                    url = [client.request(frame, output='geturl')]
                else:
                    url = re.compile('"(.+?)"').findall(url)
                url = [i for i in url if 'ok.ru' in i or 'vk.com' in i or 'openload.io' in i or 'openload.co' in i or 'oload.tv' in i][0]
                url = url.replace('openload.io', 'openload.co').replace('oload.tv', 'openload.co')

            try:
                url = 'http://ok.ru/video/%s' % urlparse.parse_qs(urlparse.urlparse(url).query)['mid'][0]
            except:
                pass

            if 'openload.co' in url: host = 'openload.co' ; direct = False ; url = [{'url': url, 'quality': 'HD'}]
            elif 'ok.ru' in url: host = 'vk' ; direct = True ; url = directstream.odnoklassniki(url)
            elif 'vk.com' in url: host = 'vk' ; direct = True ; url = directstream.vk(url)
            else: raise Exception()

            for i in url:
                sources.append({'source': host, 'quality': i['quality'], 'language': 'en', 'url': i['url'], 'direct': direct, 'debridonly': False})

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


