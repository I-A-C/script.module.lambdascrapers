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

import re,traceback,urllib,urlparse,base64
import requests

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['icouchtuner.to']
        self.base_link = 'http://ecouchtuner.to/'
        self.search_link = '?s=%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            scrape = cleantitle.geturl(tvshowtitle).replace('-','+')
            start_url = urlparse.urljoin(self.base_link, self.search_link %(scrape))

            html = client.request(start_url)
            results = client.parseDOM(html, 'div', attrs={'class':'post'})
            for content in results:
                show_url, url_text = re.compile('href="(.+?)" rel="bookmark" title="(.+?)"',re.DOTALL).findall(content)[0]
                if cleantitle.get(tvshowtitle.translate(None, ':*?"\'\.<>|&!,')) in cleantitle.get(show_url):
                    url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'url': show_url}
                    url = urllib.urlencode(url)
                    return url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('ICouchTuner - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])

            html = client.request(str(url['url']))
            results = client.parseDOM(html, 'strong')

            for content in results:
                try:
                    show_url, url_text = re.compile('href="(.+?)">(.+?)</a>',re.DOTALL).findall(content)[0]
                    # older links have "nofollow" after href, but not showing hosts on items I tested, so doesn't matter if those are "broken" for scraping.
                except:
                    continue
                chkstr = 'Season %s Episode %s' % (season, episode)
                chkstr2 = 'S%s Episode %s' % (season, episode)
                if (chkstr.lower() in url_text.lower()) or (chkstr2.lower() in url_text.lower()):
                    return show_url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('ICouchTuner - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            html = client.request(url)
            watchlink = client.parseDOM(html, 'div', attrs={'class':'entry'})[0]
            watchlink = client.parseDOM(watchlink, 'a', ret='href')[0]
            html = client.request(watchlink)

            posttabs = client.parseDOM(html, 'div', attrs={'class':'postTabs_divs'})
            for content in posttabs:
                host = re.compile('<b>(.+?)</b>',re.DOTALL).findall(content)[0]
                vid_url = client.parseDOM(content, 'iframe', ret='src')[0]
                sources.append({'source':host,'quality':'SD','language': 'en','url':vid_url,'direct':False,'debridonly':False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('ICouchTuner - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url