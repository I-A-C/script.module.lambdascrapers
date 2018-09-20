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

import urlparse, urllib, re, json, xbmc

from resources.lib.modules import client, cleantitle, source_utils, directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['123movies.as']
        self.base_link = 'https://123movies.ph/'
        self.source_link = 'https://putstream.win'
        self.episode_path = '/episodes/%s-%sx%s/'
        self.movie_path = '/movies/%s-watch-online-free-123movies/'
        self.decode_file = '/decoding_v2.php'
        self.grabber_file = '/get.php'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'title': title, 'year': year}
            return urllib.urlencode(url)

        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            data = {'tvshowtitle': tvshowtitle, 'year': year, 'imdb': imdb}
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

            if 'episode' in data:
                url = self.__get_episode_url(data)
                get_body = 'type=episode&%s=%s&imd_id=%s&seasonsNo=%02d&episodesNo=%02d'
            else:
                url = self.__get_movie_url(data)

            response = client.request(url)
            url = re.findall('<iframe .+? src="(.+?)"', response)[0]

            response = client.request(url)

            token = re.findall('var tc = \'(.+?)\'', response)[0]
            seeds = re.findall('_tsd_tsd\(s\) .+\.slice\((.+?),(.+?)\).+ return .+? \+ \"(.+?)\"\+\"(.+?)";', response)[0]
            pair = re.findall('\'type\': \'.+\',\s*\'(.+?)\': \'(.+?)\'', response)[0]

            header_token = self.__xtoken(token, seeds)
            body = 'tokenCode=' + token

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-token': header_token
            }

            url = urlparse.urljoin(self.source_link, self.decode_file)
            response = client.request(url, XHR=True, post=body, headers=headers)

            sources_dict = json.loads(response)

            for source in sources_dict:
                try:
                    if 'vidushare.com' in source:
                        sources.append({
                            'source': 'CDN',
                            'quality': 'HD',
                            'language': 'en',
                            'url': source,
                            'direct': True,
                            'debridonly': False
                        })
                except Exception:
                    pass

            body = get_body % (pair[0], pair[1], data['imdb'], int(data['season']), int(data['episode']))

            url = urlparse.urljoin(self.source_link, self.grabber_file)
            response = client.request(url, XHR=True, post=body, headers=headers)

            sources_dict = json.loads(response)

            for source in sources_dict:
                try:
                    quality = source_utils.label_to_quality(source['label'])
                    link = source['file']

                    if 'lh3.googleusercontent' in link:
                        link = directstream.googleredirect(link)

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


            return sources

        except Exception:
            return sources

    def resolve(self, url):
        return url

    def __get_episode_url(self, data):
        try:
            clean_title = cleantitle.geturl(data['tvshowtitle'])
            query = self.episode_path % (clean_title, data['season'], data['episode'])

            url = urlparse.urljoin(self.base_link, query)
            html = client.request(url)

            token = re.findall('\/?watch-token=(.*?)\"', html)[0]

            return url + ('?watch-token=%s' % token)

        except Exception:
            return

    def __get_movie_url(self, data):
        pass

    def __xtoken(self, token, seeds):
        try:
            xtoken = token[int(seeds[0]):int(seeds[1])]
            xtoken = list(xtoken)
            xtoken.reverse()

            return ''.join(xtoken) + seeds[2] + seeds[3]

        except Exception:
            return
