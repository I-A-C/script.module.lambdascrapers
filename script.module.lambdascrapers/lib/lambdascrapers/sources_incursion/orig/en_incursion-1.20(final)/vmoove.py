# -*- coding: utf-8 -*-

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

from bs4 import BeautifulSoup
from resources.lib.modules import directstream, source_utils
import requests, re, sys, traceback


class source:

    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domain = 'vmovee.me'
        self.base_link = 'https://vmovee.me'
        self.search_link = '/gold-app/gold-includes/GOLD.php?seasons_post_name='
        self.search_episode_link = '/gold-app/gold-includes/GOLD.php?season_id='
        self.movie_link = ''
        self.episode_link = '/gold-app/gold-includes/GOLD.php?episode_id='
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
                # NOW SCRAPPING EPISODES
                soup = BeautifulSoup(p.text, 'html.parser')
                episode_link_list = soup.findAll('div', {'class':'episode-item'})
                url = None
                for i in episode_link_list:
                    remoteEpNum = i.find('div', {'class':'episode-number'}).find('span').text
                    if remoteEpNum == episode:
                        url = re.findall(r'\((\d*)\)', i.find('a').prettify())[0]

            return url
        except:
            traceback.print_exc()
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
            traceback.print_exc()()

        return sources

    def resolve(self, url):
        return url
