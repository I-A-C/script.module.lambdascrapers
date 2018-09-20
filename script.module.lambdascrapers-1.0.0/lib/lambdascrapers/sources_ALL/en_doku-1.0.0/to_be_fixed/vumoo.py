"""
    Covenant Add-on

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
"""

import urlparse, urllib, json, base64, hashlib, re, xbmc, requests

from resources.lib.modules import client, cleantitle, source_utils, directstream
from resources.lib.modules import pyaes


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vumoo.to']
        self.base_link = 'http://vumoo.to'
        self.cdn_link = 'http://cdn.123moviesapp.net'
        self.search_path = '/search?q=%s'
        self.password = 'iso10126'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title).replace('-','+')
            url = {'title': title, 'year': year, 'imdb': imdb, 'clean_title': clean_title}
            return urllib.urlencode(url)

        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            data = {'tvshowtitle': tvshowtitle, 'year': year, 'imdb': imdb, 'clean_title':cleantitle.geturl(tvshowtitle).replace('-','+')}
            return urllib.urlencode(data)

        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)
            data.update({'season': season, 'episode': episode, 'title': title, 'premiered': premiered})

            return urllib.urlencode(data)

        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)

            if 'tvshowtitle' in data:
                urls = self.__get_episode_urls(data)
            else:
                urls = self.__get_movie_urls(data)

            for url in urls:
                response = requests.get(url).text

                encrypted = re.findall('embedVal="(.+?)"', response)[0]
                decrypted = self.__decrypt(encrypted)

                storage = json.loads(decrypted)

                for location in storage['videos']:
                    if 'sources' in location:
                        for source in location['sources']:
                            try:
                                link = source['file']

                                if 'google' in link or 'blogspot' in link:
                                    quality = directstream.googletag(link)[0]['quality']

                                    if 'lh3.googleusercontent' in link:
                                        link = directstream.googleproxy(link)

                                    sources.append({
                                        'source': 'gvideo',
                                        'quality': quality,
                                        'language': 'en',
                                        'url': link,
                                        'direct': True,
                                        'debridonly': False
                                    })

                                else:
                                    continue

                            except Exception:
                                continue

                    elif 'url' in location:
                        if 'openload' in location['url']:
                            quality = storage['video'] if 'tvshowtitle' not in data else '720p'
                            sources.append(
                                {'source': "openload.co",
                                 'quality': quality,
                                 'language': "en",
                                 'url': location['url'],
                                 'direct': False,
                                 'debridonly': False})
                        else:
                            url = urlparse.urljoin(self.cdn_link, location['url'])

                            response = requests.get(url).text
                            try:
                                manifest = json.loads(response)
                                for video in manifest:
                                    try:
                                        quality = video['label'] if video['label'] == '720p' or video['label'] == '1080p' else  'SD'
                                        link = video['file']

                                        sources.append({
                                            'source': 'CDN',
                                            'quality': quality,
                                            'language': 'en',
                                            'url': link,
                                            'direct': True,
                                            'debridonly': False
                                        })

                                    except Exception:
                                        continue
                            except Exception:
                                continue

            return sources

        except Exception:
            return

    def resolve(self, url):
        try:
            return url

        except Exception:
            return

    def __get_episode_urls(self, data):
        try:
            search = self.search_path % data['clean_title']+ '+season+'+data['season']
            url = urlparse.urljoin(self.base_link, search)

            response = client.request(url)

            jsobj = json.loads(response)

            for obj in jsobj['suggestions']:
                if data['tvshowtitle'] in obj['value'] and data['season'] in obj['value']:
                    url = urlparse.urljoin(self.base_link, obj['data']['href'])

            response = client.request(url)

            urls = re.findall('embedUrl="([^<]*?)">s%02de%02d<' % (int(data['season']), int(data['episode'])), response)

            return urls

        except Exception:
            return

    def __get_movie_urls(self, data):
        try:
            search = self.search_path % data['clean_title']+ '+'+data['year']
            url = urlparse.urljoin(self.base_link, search)

            response = client.request(url)

            jsobj = json.loads(response)

            path = jsobj['suggestions'][0]['data']['href']
            url = urlparse.urljoin(self.base_link, path)

            response = client.request(url)

            urls = re.findall('embedUrl="(.+?)">', response)

            return urls

        except Exception:
            return

    def __bytes_to_key(self, password, salt, output=48):
        try:
            seed = hashlib.md5(password + salt).digest()
            key = seed

            while len(key) < output:
                seed = hashlib.md5(seed + (password + salt)).digest()
                key += seed

            return key[:output]

        except Exception:
            return


    def __decrypt(self, encrypted):
        try:
            encrypted = base64.b64decode(encrypted)

            salt = encrypted[8:16]

            key_iv = self.__bytes_to_key(self.password, salt)

            key = key_iv[:32]
            iv = key_iv[32:]

            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv = iv))
            plaintext = decrypter.feed(encrypted[16:])
            plaintext += decrypter.feed()

            return plaintext

        except Exception:
            return
