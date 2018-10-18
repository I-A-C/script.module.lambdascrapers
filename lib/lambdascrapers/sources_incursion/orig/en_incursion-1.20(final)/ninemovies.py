'''
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

'''
import re
import urllib
import urlparse
import json
import ast
import xbmc
import httplib

from resources.lib.modules import client, cleantitle, directstream, jsunpack, source_utils


class source:
    def __init__(self):
        '''
        Constructor defines instances variables

        '''
        self.priority = 1
        self.language = ['en']
        self.domains = ['fmovies.se', 'fmovies.to', 'bmovies.to', 'bmovies.is']
        self.base_link = 'https://bmovies.is'
        self.search_path = '/search?keyword=%s'
        self.film_path = '/film/%s'
        self.js_path = '/assets/min/public/all.js?5a0da8a9'
        self.info_path = '/ajax/episode/info?ts=%s&_=%s&id=%s&server=%s&update=0'
        self.grabber_path = '/grabber-api/?ts=%s&id=%s&token=%s&mobile=0'

    def movie(self, imdb, title, localtitle, aliases, year):
        '''
        Takes movie information and returns a set name value pairs, encoded as
        url params. These params include ts
        (a unqiue identifier, used to grab sources) and list of source ids

        Keyword arguments:

        imdb -- string - imdb movie id
        title -- string - name of the movie
        localtitle -- string - regional title of the movie
        year -- string - year the movie was released

        Returns:

        url -- string - url encoded params

        '''
        try:
            clean_title = cleantitle.geturl(title)
            query = (self.search_path % clean_title)
            url = urlparse.urljoin(self.base_link, query)

            search_response = client.request(url)

            results = client.parseDOM(search_response,
                'div', attrs={'class': 'row movie-list'})[0]

            search = '=\"(ajax\/film\/tooltip\/.*?)\".*?class=\"name\" href=\"\/film\/(.*?)\.(.*?)\">'
            results_info = re.findall(search, results)

            results_list = []

            for result in results_info:
                if(result[1] == clean_title):
                    results_list.append({'title': result[1], 'id': result[2], 'info': result[0]})

            if(len(results_list) > 1):
                for result in results_list:
                    url = urlparse.urljoin(self.base_link, '/' + result['info'])
                    tooltip = client.request(url, XHR=True)

                    date = re.findall('<span>(\d{4})</span>', tooltip)[0]

                    if date == str(year):
                        result_dict = result
                        break

            else:
                result_dict = results_list[0]

            query = self.film_path % (result_dict['title'] + '.' + result_dict['id'])
            url = urlparse.urljoin(self.base_link, query)

            source_response = client.request(url)

            ts = re.findall('data-ts=\"(.*?)\">', source_response)[0]

            servers = client.parseDOM(
                source_response, 'div', attrs={'id': 'servers'})[0]
            servers = servers.split('</li> </ul> </div> </div>')

            sources_list = []

            for i in servers:
                try:
                    source_id = re.findall('\/(.{6})">', i)[0]
                    source_server = re.findall('data-id=\"(\d{2})\"', i)[0]

                    sources_list.append((source_id, source_server))
                except Exception:
                    pass

            data = {
                'imdb': imdb,
                'title': title,
                'localtitle': localtitle,
                'year': year,
                'ts': ts,
                'sources': sources_list
            }
            url = urllib.urlencode(data)

            return url

        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        '''
        Takes TV show information, encodes it as name value pairs, and returns
        a string of url params

        Keyword arguments:

        imdb -- string - imdb tv show id
        tvdb -- string - tvdb tv show id
        tvshowtitle -- string - name of the tv show
        localtvshowtitle -- string - regional title of the tv show
        year -- string - year the tv show was released

        Returns:

        url -- string - url encoded params

        '''
        try:
            data = {
                'imdb': imdb,
                'tvdb': tvdb,
                'tvshowtitle': tvshowtitle,
                'year': year
            }
            url = urllib.urlencode(data)

            return url

        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        '''
        Takes episode information, finds the ts and list sources, encodes it as
        name value pairs, and returns a string of url params

        Keyword arguments:

        url -- string - url params
        imdb -- string - imdb tv show id
        tvdb -- string - tvdb tv show id
        title -- string - episode title
        premiered -- string - date the episode aired (format: year-month-day)
        season -- string - the episodes season
        episode -- string - the episode number

        Returns:

        url -- string - url encoded params

        '''
        try:
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)

            clean_title = cleantitle.geturl(data['tvshowtitle'])
            query = (self.search_path % clean_title)
            url = urlparse.urljoin(self.base_link, query)

            search_response = client.request(url)

            results_list = client.parseDOM(
                search_response, 'div', attrs={'class': 'row movie-list'})[0]

            film_id = ''

            film_tries = [
             '\/film\/(' + (clean_title + '-0' + season) + '[^-0-9].+?)\"',
             '\/film\/(' + (clean_title + '-' + season) + '[^-0-9].+?)\"',
             '\/film\/(' + clean_title + '[^-0-9].+?)\"'
             ]

            for i in range(len(film_tries)):
                if not film_id:
                    film_id = re.findall(film_tries[i], results_list)
                else:
                    break

            film_id = film_id[0]

            query = (self.film_path % film_id)
            url = urlparse.urljoin(self.base_link, query)

            film_response = client.request(url)

            ts = re.findall('(data-ts=\")(.*?)(\">)', film_response)[0][1]

            servers = client.parseDOM(
                film_response, 'div', attrs={'id': 'servers'})[0]

            servers = servers.split('</li> </ul> </div> </div>')

            if not re.findall(
             '([^\/]*)\">' + episode + '[^0-9]', servers[0]):
                episode = '%02d' % int(episode)

            sources_list = []

            for i in servers:
                try:
                    source_id = re.findall(
                        ('([^\/]*)\">' + episode + '[^0-9]'), i)[0]
                    source_server = re.findall('data-id=\"(.*?)\"', i)[0]

                    sources_list.append((source_id, source_server))
                except Exception:
                    pass

            data.update({
                'title': title,
                'premiered': premiered,
                'season': season,
                'episode': episode,
                'ts': ts,
                'sources': sources_list
            })

            url = urllib.urlencode(data)

            return url

        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        '''
        Loops over site sources and returns a dictionary with corresponding
        file locker sources and information

        Keyword arguments:

        url -- string - url params

        Returns:

        sources -- string - a dictionary of source information

        '''

        sources = []

        try:
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)

            data['sources'] = ast.literal_eval(data['sources'])

            for i in data['sources']:
                try:
                    token = str(self.__token(
                        {'id': i[0], 'update': '0', 'ts': data['ts'], 'server': i[1]}))

                    query = (self.info_path % (data['ts'], token, i[0], i[1]))
                    url = urlparse.urljoin(self.base_link, query)

                    info_response = client.request(url, headers={'Referer': self.base_link}, XHR=True)

                    info_dict = json.loads(info_response)

                    if info_dict['type'] == 'direct':
                        token64 = info_dict['params']['token']
                        query = (self.grabber_path % (data['ts'], i[0], self.__decode_shift(token64, -18)))
                        url = urlparse.urljoin(self.base_link, query)
                        response = client.request(url, XHR=True)

                        grabber_dict = json.loads(response)

                        if not grabber_dict['error'] == None:
                            continue

                        sources_list = grabber_dict['data']

                        for j in sources_list:
                            try:
                                quality = source_utils.label_to_quality(j['label'])
                                link = j['file']

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

                            except Exception:
                                pass

                    elif info_dict['type'] == 'iframe':
                        # embed = self.__decode_shift(info_dict['target'], -18)
                        embed = info_dict['target']

                        valid, hoster = source_utils.is_host_valid(embed, hostDict)
                        if not valid: continue

                        headers = {
                            'Referer': self.base_link
                        }

                        embed = embed + source_utils.append_headers(headers)

                        sources.append({
                            'source': hoster,
                            'quality': '720p', # need a better way of identifying quality
                            'language': 'en',
                            'url': embed,
                            'direct': False,
                            'debridonly': False
                        })

                except Exception:
                    pass

            return sources

        except Exception:
            return sources

    def resolve(self, url):
        '''
        Takes a scraped url and returns a properly formatted url

        Keyword arguments:

        url -- string - source scraped url

        Returns:

        url -- string - a properly formatted url

        '''
        try:
            return url

        except Exception:
            return

    def __token(self, dic):
        '''
        Takes a dictionary containing id, update, server, and ts, then returns
        a token which is used by info_path to retrieve grabber api
        information

        Thanks to coder-alpha for the updated bitshifting obfuscation
        https://github.com/coder-alpha

        Keyword arguments:

        d -- dictionary - containing id, update, ts, server

        Returns:

        token -- integer - a unique integer
        '''
        def bitshifthex(t, e):
            i = 0
            n = 0

            for i in range(0, max(len(t), len(e))):
        		if i < len(e):
        			n += ord(e[i])
        		if i < len(t):
        			n += ord(t[i])

            h = format(int(hex(n),16),'x')
            return h

        def bitshiftadd(t):
            i = 0

            for e in range(0, len(t)):
            	i += ord(t[e]) + e

            return i

        try:
            url = urlparse.urljoin(self.base_link, self.js_path)
            response = client.request(url)

            unpacked = jsunpack.unpack(response)

            phrase = 'function\(t,\s*i,\s*n\)\s*{\s*"use strict";\s*function e\(\)\s*{\s*return (.*?)\s*}\s*function r\(t\)'

            seed_var = re.findall(r'%s' % phrase, unpacked)[0]
            seed = re.findall(r'%s=.*?\"(.*?)\"' % seed_var, unpacked)[0]

            token = bitshiftadd(seed)

            for i in dic:
                token += bitshiftadd(bitshifthex(seed + i, dic[i]))

            return str(token)

        except Exception:
            return

    def __decode_shift(self, t, i):
        '''
        Takes a bitshifted String and removes bitshifting obfuscation

        Thanks to coder-alpha for the bitshifting algorithm
        https://github.com/coder-alpha

        Keyword arguments:

        t -- string - the obfuscated string
        i -- int -  the bitshift offset

        Returns:

        url -- string - the unobfuscated string
        '''
        try:
            n = []
            e = []
            r = ''

            for n in range(0, len(t)):
                if n == 0 and t[n] == '.':
                    pass
                else:
                    c = ord(t[n])
                    if c >= 97 and c <= 122:
                        e.append((c - 71 + i) % 26 + 97)
                    elif c >= 65 and c <= 90:
                        e.append((c - 39 + i) % 26 + 65)
                    else:
                        e.append(c)
            for ee in e:
    			r += chr(ee)

            return r

        except Exception:
            return
