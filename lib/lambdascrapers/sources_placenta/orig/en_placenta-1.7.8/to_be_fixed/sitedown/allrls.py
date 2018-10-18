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

import re,traceback,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['allrls.co']
        self.base_link = 'http://bestrls.net/'
        self.search_link = '?s=%s+%s&go=Search'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            pages = []
            scrape_title = cleantitle.geturl(title).replace('-', '+')
            start_url = urlparse.urljoin(self.base_link, self.search_link % (scrape_title, year))

            html = client.request(start_url)
            results = client.parseDOM(html, 'h2', attrs={'class':'entry-title'})
            for content in results:
                found_link = client.parseDOM(content, 'a', ret='href')[0]
                if self.base_link in found_link:
                    if cleantitle.get(title) in cleantitle.get(found_link):
                        if year in found_link:
                            pages.append(found_link)
            return pages
        except:
            failure = traceback.format_exc()
            log_utils.log('ALLRLS - Exception: \n' + str(failure))
            return pages

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            data = {'tvshowtitle': tvshowtitle, 'year': year}
            return urllib.urlencode(data)
        except:
            failure = traceback.format_exc()
            log_utils.log('ALLRLS - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            pages = []
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)
            data.update({'season': season, 'episode': episode, 'title': title, 'premiered': premiered})

            season_base = 'S%02dE%02d' % (int(data['season']), int(data['episode']))
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', season_base)
            tvshowtitle = data['tvshowtitle']
            tvshowtitle = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', tvshowtitle)

            query = query.replace("&", "and")
            query = query.replace("  ", " ")
            query = query.replace(" ", "+")
            tvshowtitle = tvshowtitle.replace("&", "and")
            tvshowtitle = tvshowtitle.replace("  ", " ")
            tvshowtitle = tvshowtitle.replace(" ", "+")

            start_url = urlparse.urljoin(self.base_link, self.search_link % (tvshowtitle, query))

            html = client.request(start_url)
            results = client.parseDOM(html, 'h2', attrs={'class':'entry-title'})
            for content in results:
                found_link = client.parseDOM(content, 'a', ret='href')[0]
                if self.base_link in found_link:
                    if cleantitle.get(data['tvshowtitle']) in cleantitle.get(found_link):
                        if cleantitle.get(season_base) in cleantitle.get(found_link):
                            pages.append(found_link)
            return pages
        except:
            failure = traceback.format_exc()
            log_utils.log('ALLRLS - Exception: \n' + str(failure))
            return pages

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            hostDict = hostprDict + hostDict
            pages = url
            for page_url in pages:
                r = client.request(page_url)
                urls = client.parseDOM(r, 'a', ret = 'href')
                for url in urls:
                    try:
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                        if not host in hostDict: raise Exception()

                        if any(x in url for x in ['.rar', '.zip', '.iso']): continue

                        quality, info = source_utils.get_release_quality(url)

                        info = []

                        if any(x in url.upper() for x in ['HEVC', 'X265', 'H265']): info.append('HEVC')

                        info = ' | '.join(info)

                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False})
                    except:
                        pass
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('ALLRLS - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
