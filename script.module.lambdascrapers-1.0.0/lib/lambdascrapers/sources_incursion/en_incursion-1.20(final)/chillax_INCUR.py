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

import requests
import json,sys
from resources.lib.modules import control
import inspect

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domain = 'chillax.ws'
        self.base_link = 'http://chillax.ws'
        self.search_link = 'http://chillax.ws/search/auto?q='
        self.movie_link = "http://chillax.ws/movies/getMovieLink?"
        self.login_link = 'http://chillax.ws/session/login?return_url=/index'
        self.tv_link = 'http://chillax.ws/series/getTvLink?'
        self.login_payload = {'username': control.setting('chillax.username'),'password':control.setting('chillax.password')}
        if self.login_payload['username'] == '':
            self.login_payload = {'username': 'notreal33','password':'notreal3333'}

    def movie(self, imdb, title, localtitle, aliases, year):
        url = {'imdb': imdb, 'title': title, 'year': year}
        with requests.Session() as s:
            p = s.post(self.login_link, self.login_payload)
            p = s.get(self.search_link + title)
            show_dict = json.loads(p.text)
            for i in show_dict:
                if i['title'].lower() == title.lower() and i['year'] == year:
                    show_dict = i
                    break
            p = s.post(self.movie_link + "id=%s" % show_dict['id'])
            url = json.loads(p.text)
            sources = []
            for i in url:
                video = {}
                p = s.head(self.base_link + i['file'])
                vurl = p.headers['Location']
                print(p.headers['Location'])
                video['url'] = vurl
                video['quality'] = i['label']
                video['source'] = 'gvideo'
                video['debridonly'] = False
                video['language'] = 'en'
                video['info'] = i['type']
                video['direct'] = True
                sources.append(video)

        return sources


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle
            return url
        except:
            print("Unexpected error in Chillax Script:", sys.exc_info()[0])
            return ""

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
         with requests.Session() as s:
            p = s.post(self.login_link, self.login_payload)
            search_text = url
            p = s.get(self.search_link + search_text)
            show_dict = json.loads(p.text)
            for i in show_dict:
                if i['title'].lower() == search_text.lower():
                    show_dict = i
                    break
            url = {'title': search_text, 'id': show_dict['id'], 'season': season, 'episode': episode}
            link = self.tv_link + "id=%s&s=%s&e=%s" % (url["id"], url['season'], url['episode'])
            p = s.post(link)
            url = json.loads(p.text)
            sources = []
            for i in url:
                video = {}
                p = s.head(self.base_link + i['file'])
                vurl = p.headers['Location']
                video['url'] = vurl
                video['quality'] = i['label']
                video['source'] = 'gvideo'
                video['debridonly'] = False
                video['language'] = 'en'
                video['info'] = i['type']
                video['direct'] = True
                sources.append(video)
            return sources

    def sources(self, url, hostDict, hostprDict):
        return url

    def resolve(self, url):
            return url

