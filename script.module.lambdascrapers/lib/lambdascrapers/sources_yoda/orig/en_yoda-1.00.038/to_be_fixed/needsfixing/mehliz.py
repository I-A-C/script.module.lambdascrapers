# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Yoda
# Addon id: plugin.video.Yoda
# Addon Provider: MuadDib

import urlparse, urllib, re, json, xbmc, httplib

from resources.lib.modules import client, cleantitle, source_utils, directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['mehlizmovies.is']
        self.base_link = 'https://www.mehlizmovies.is'
        self.season_path = '/seasons/%s-season-%s/'
        self.search_path = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'title': title, 'year': year}
            return urllib.urlencode(url)

        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            data = {'tvshowtitle': tvshowtitle, 'year': year}
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
                url = self.__get_episode_url(data)
            else:
                url = self.__get_movie_url(data)

            urls = []

            if isinstance(url, str):
                urls.append(url)
            else:
                urls.extend(url)

            for url in urls:
                if 'mehlizmovies.is' in url:
                    html = client.request(url, referer=self.base_link + '/')
                    files = re.findall('file: \"(.+?)\".+?label: \"(.+?)\"', html)

                    for i in files:
                        try:
                            sources.append({
                                'source': 'gvideo',
                                'quality': i[1],
                                'language': 'en',
                                'url': i[0],
                                'direct': True,
                                'debridonly': False
                            })

                        except Exception:
                            pass

                else:
                    valid, hoster = source_utils.is_host_valid(url, hostDict)
                    if not valid: continue
                    urls, host, direct = source_utils.check_directstreams(url, hoster)

                    sources.append({
                        'source': hoster,
                        'quality': urls[0]['quality'],
                        'language': 'en',
                        'url': url,
                        'direct': False,
                        'debridonly': False
                    })

            return sources

        except Exception:
            return

    def resolve(self, url):
        try:
            return url
        except Exception:
            return

    def __get_episode_url(self, data):
        try:
            value = data['tvshowtitle'].lower().replace(' ', '+') + '+season+' + data['season']
            query = self.search_path % value
            url = urlparse.urljoin(self.base_link, query)

            # Gzip returns IncompleteRead
            html = client.request(url, compression=False)

            url = re.findall('\"title\">\s<a href=\"(.+?)\">%s: Season %s<\/a>' % (data['tvshowtitle'], data['season']), html, re.IGNORECASE)[0]

            html = client.request(url)
            page_list = re.findall('\"numerando\">%sx%s<\/div>\s+.+\s+.+?href=\"(.+?)\">(.+?)<\/a>' % (data['season'], data['episode']), html)

            if len(page_list) > 1:
                ref_title = data['title'].lower().replace(' ', '')

                for i in page_list:
                    found_title = i[1].lower().replace(' ', '')

                    if found_title == ref_title:
                        ep_page = i[0]
                        break

            else:
                ep_page = page_list[0][0]

            html = client.request(ep_page)
            embed = re.findall('<iframe.+?src=\"(.+?)\"', html)[0]

            return embed

        except Exception:
            return

    def __get_movie_url(self, data):
        try:
            query = self.search_path % data['title'].lower().replace(' ', '+')
            url = urlparse.urljoin(self.base_link, query)

            # Gzip returns IncompleteRead
            html = client.request(url, compression=False)

            pages = re.findall('<div class="title">\s<a href="(.+?)">%s.+?\/a>' % data['title'], html)

            embeds = []

            for page in pages:
                html = client.request(page)
                embeds.append(re.findall('play-box-iframe.+\s<iframe.+?src=\"(.+?)\"', html)[0])

            if len(embeds) > 1:
                return embeds
            else:
                return embeds[0]

        except Exception:
            return
