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

import requests,traceback,re,sys

from bs4 import BeautifulSoup
from resources.lib.modules import directstream
from resources.lib.modules import source_utils

class source:

    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'vmovee.xyz'
        self.base_link = 'https://vmovee.xyz'
        self.search_link = '/search?q=%s&x=0&y=0'
        self.search_episode_link = '/search?q=%s&x=0&y=0'
        self.movie_link = '/search?q=%s&x=0&y=0'
        self.episode_link = '/search?q=%s&x=0&y=0'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        tvshowtitle = tvshowtitle.replace(" ", "-")
        url = tvshowtitle
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if not url:
            return url
        try:
            with requests.session() as s:

                p = s.get(self.base_link + self.search_link + url, headers=self.headers)
                if p.text == '':
                    p = s.get(self.base_link + self.search_link + url + "-all-seasons", headers=self.headers)
                    if p.text == '':
                        return url

                soup = BeautifulSoup(p.text, 'html.parser')
                season_link_list = soup.findAll('div', {'class':'episode-item'})
                season_id = None
                for i in season_link_list:
                    if i.find('span').text == 'Season %s' % season:
                        season_id = re.findall(r'\((\d*)\)', i.find('a').prettify())[0]

                p = s.get(self.base_link + self.search_episode_link + season_id, headers=self.headers)

                soup = BeautifulSoup(p.text, 'html.parser')
                episode_link_list = soup.findAll('div', {'class':'episode-item'})
                url = None
                for i in episode_link_list:
                    remoteEpNum = i.find('div', {'class':'episode-number'}).find('span').text
                    if remoteEpNum == episode:
                        url = re.findall(r'\((\d*)\)', i.find('a').prettify())[0]

            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('Vmovee - Exception: \n' + str(failure))
        return url

    def sources(self, url, hostDict, hostprDict):
        hostDict = hostDict + hostprDict
        sources = []
        if url is None:
            return sources

        try:
            with requests.Session() as s:
                p = s.get(self.base_link + self.episode_link + url, headers=self.headers)
                soup = BeautifulSoup(p.text, 'html.parser')
                src = soup.find('iframe')
                url = src['src']

                if '//apu,litaurl.com/' in url:
                    p = s.headers(url)
                    url = p.url

                valid, host = source_utils.checkHost(url, hostDict)
                quality = source_utils.get_quality_simple(url)

                if valid == True:
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': '',
                     'direct': False,
                     'debridonly': True})
        except:
            failure = traceback.format_exc()
            log_utils.log('Vmovee - Exception: \n' + str(failure))

        return sources

    def resolve(self, url):
        return url
