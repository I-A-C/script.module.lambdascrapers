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

import re
import urllib
import urlparse

from resources.lib.modules import cache
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser
from resources.lib.modules import cfscrape

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['breakfreemovies.biz']
        self.base_link = 'https://alphareign.lol/'
        self.search_link = '/movies.php?list=search&search=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            scraper = cfscrape.create_scraper()
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url  % (title.replace(':', ' ').replace(' ', '+'))

            search_results = client.request(url)
            tr_list = re.compile('(?i)<tr id="coverPreview.+?">(.+?)<\/tr>',re.DOTALL).findall(search_results)
            for row in tr_list:
                row_url = re.compile('href="(.+?)"',re.DOTALL).findall(row)[0]
                row_title = re.compile('href=".+?">(.+?)</a>',re.DOTALL).findall(row)[0]
                if cleantitle.get(title) in cleantitle.get(row_title):
                    if year in str(row):
                        ret_url = urlparse.urljoin(self.base_link, row_url)
                        return ret_url
            return
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            html = client.request(url)
            html = html.replace('\\"', '"')

            sources = self.get_hoster_list(html, sources, hostDict)

            links = dom_parser.parse_dom(html, 'tr', attrs={'id': 'tablemoviesindex2'})

            for i in links:
                try:
                    host = dom_parser.parse_dom(i, 'img', req='alt')[0].attrs['alt']
                    host = host.split()[0].rsplit('.', 1)[0].strip().lower()
                    host = host.encode('utf-8')

                    valid, host = source_utils.is_host_valid(host, hostDict)
                    if not valid: continue

                    url = dom_parser.parse_dom(i, 'a', req='href')[0].attrs['href']
                    url = client.replaceHTMLCodes(url)
                    url = urlparse.urljoin(self.base_link, url)
                    url = url.encode('utf-8')
                    selected_url = client.request(url)
                    Links = re.compile('href="(.+?)"',re.DOTALL).findall(selected_url)
                    for link in Links:
                        if host.lower() in link.lower():
                            sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources

    def get_hoster_list(self, html, sources, hostDict):
        try:
            if html == None: return sources
            hoster_box = re.compile('(?i)<select name="hosterlist"(.+?)select>',re.DOTALL).findall(html)[0]
            options = re.compile('(?i)<option value="(.+?)"',re.DOTALL).findall(hoster_box)
            for url in options:
                url = urlparse.urljoin(self.base_link, url)
                url_html = client.request(url)
                vid_div = re.compile('(?i)<div style="width:742px">(.+?)<\/a>',re.DOTALL).findall(url_html)[0]
                vid_url = re.compile('(?i)<a target="_blank" href="(.+?)"',re.DOTALL).findall(vid_div)[0]
                valid, host = source_utils.is_host_valid(vid_url, hostDict)
                if not valid: continue
                sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': vid_url, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url