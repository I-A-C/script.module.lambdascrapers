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

import json,re,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['1movies.se','1movies.to']
        self.base_link = 'https://1movies.se'
        self.search_link = '/search_all/%s'
        self.player_link = '/ajax/movie/load_player_v3'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            return self.__search([title] + source_utils.aliases_to_array(aliases), year)
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'tvshowtitle': tvshowtitle, 'aliases': aliases, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            url = self.__search([data['tvshowtitle']] + source_utils.aliases_to_array(eval(data['aliases'])), data['year'], season)
            if not url: return

            r = client.request(urlparse.urljoin(self.base_link, url))

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'ep_link'})
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [(i.attrs['href'], i.content) for i in r if i]
            r = [(i[0], re.findall("^(?:episode)\s*(\d+)$", i[1], re.I)) for i in r]
            r = [(i[0], i[1][0] if i[1] else '0') for i in r]
            r = [i[0] for i in r if int(i[1]) == int(episode)][0]

            return source_utils.strip_domain(r)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            ref = urlparse.urljoin(self.base_link, url)

            r = client.request(ref)

            p = re.findall('load_player\((\d+)\)', r)
            r = client.request(urlparse.urljoin(self.base_link, self.player_link), post={'id': p[0]}, referer=ref, XHR=True)
            url = json.loads(r).get('value')
            link = client.request(url, XHR=True, output='geturl', referer=ref)

            if '1movies.' in link:
                r = client.request(link, XHR=True, referer=ref)
                r = [(match[1], match[0]) for match in re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', r, re.DOTALL)]
                r = [(re.sub('[^\d]+', '', x[0]), x[1].replace('\/', '/')) for x in r]
                r = [x for x in r if x[0]]

                links = [(x[1], '4K') for x in r if int(x[0]) >= 2160]
                links += [(x[1], '1440p') for x in r if int(x[0]) >= 1440]
                links += [(x[1], '1080p') for x in r if int(x[0]) >= 1080]
                links += [(x[1], 'HD') for x in r if 720 <= int(x[0]) < 1080]
                links += [(x[1], 'SD') for x in r if int(x[0]) < 720]

                for url, quality in links:
                    sources.append({'source': 'gvideo', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
            else:
                valid, host = source_utils.is_host_valid(link, hostDict)
                if not valid: return

                urls = []
                if 'google' in link: host = 'gvideo'; direct = True; urls = directstream.google(link);
                if 'google' in link and not urls and directstream.googletag(link): host = 'gvideo'; direct = True; urls = [{'quality': directstream.googletag(link)[0]['quality'], 'url': link}]
                elif 'ok.ru' in link: host = 'vk'; direct = True; urls = directstream.odnoklassniki(link)
                elif 'vk.com' in link:  host = 'vk'; direct = True; urls = directstream.vk(link)
                else:  direct = False; urls = [{'quality': 'HD', 'url': link}]

                for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
       return url

    def __search(self, titles, year, season='0'):
        try:
            query = self.search_link % (urllib.quote_plus(titles[0]))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'list_movies'})
            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'item_movie'})
            r = dom_parser.parse_dom(r, 'h2', attrs={'class': 'tit'})
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [(i.attrs['href'], i.content.lower()) for i in r if i]
            r = [(i[0], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
            r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
            r = [(i[0], i[1], i[2], re.findall('(.+?)\s+(?:\s*-?\s*(?:season|s))\s*(\d+)', i[1])) for i in r]
            r = [(i[0], i[3][0][0] if len(i[3]) > 0 else i[1], i[2], i[3][0][1] if len(i[3]) > 0 else '0') for i in r]
            r = [(i[0], i[1], i[2], '1' if int(season) > 0 and i[3] == '0' else i[3]) for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y and int(i[3]) == int(season)][0]

            return source_utils.strip_domain(r)
        except:
            return
