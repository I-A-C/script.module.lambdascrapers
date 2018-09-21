'# -*- coding: UTF-8 -*-
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
import json

from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import directstream
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['putlockertv.to']
        self.base_link = 'https://www2.putlockertv.to/'
        self.movie_search_path = ('search?keyword=%s')
        self.episode_search_path = ('/filter?keyword=%s&sort=post_date:Adesc'
                                    '&type[]=series')
        self.film_path = '/watch/%s'
        self.info_path = '/ajax/episode/info?ts=%s&_=%s&id=%s&server=28&update=0'
        self.grabber_path = '/grabber-api/?ts=%s&id=%s&token=%s&mobile=0'
        self.tooltip_path = '/ajax/film/tooltip/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            query = (self.movie_search_path % (clean_title))
            url = urlparse.urljoin(self.base_link, query)

            search_response = client.request(url)

            results_list = client.parseDOM(
                search_response, 'div', attrs={'class': 'item'})[0]
            film_id = re.findall('(\/watch\/)([^\"]*)', results_list)[0][1]

            query = (self.film_path % film_id)
            url = urlparse.urljoin(self.base_link, query)

            film_response = client.request(url)
                        
            ts = re.findall('(data-ts=\")(.*?)(\">)', film_response)[0][1]

            sources_dom_list = client.parseDOM(
                film_response, 'ul', attrs={'class': 'episodes range active'})
            sources_list = []
            
            for i in sources_dom_list:
                source_id = re.findall('([\/])(.{0,6})(\">)', i)[0][1]
                sources_list.append(source_id)
            
            servers_dom_list = client.parseDOM(
                film_response, 'div', attrs={'class': 'server row'})
            servers_list = []
            
            data = {
                'imdb': imdb,
                'title': title,
                'localtitle': localtitle,
                'year': year,
                'ts': ts,
                'sources': sources_list,
                'id': film_id
            }
            url = urllib.urlencode(data)

            return url

        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
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
        try:
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)

            clean_title = cleantitle.geturl(data['tvshowtitle'])
            query = (self.movie_search_path % clean_title)
            url = urlparse.urljoin(self.base_link, query)

            search_response = client.request(url)

            results_list = client.parseDOM(
                search_response, 'div', attrs={'class': 'items'})[0]

            film_id = []

            film_tries = [
             '\/' + (clean_title + '-0' + season) + '[^-0-9](.+?)\"',
             '\/' + (clean_title + '-' + season) + '[^-0-9](.+?)\"',
             '\/' + clean_title + '[^-0-9](.+?)\"'
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

            sources_dom_list = client.parseDOM(
                film_response, 'ul', attrs={'class': 'episodes range active'})

            if not re.findall(
             '([^\/]*)\">' + episode + '[^0-9]', sources_dom_list[0]):
                episode = '%02d' % int(episode)

            sources_list = []

            for i in sources_dom_list:
                source_id = re.findall(
                    ('([^\/]*)\">' + episode + '[^0-9]'), i)[0]
                sources_list.append(source_id)

            data.update({
                'title': title,
                'premiered': premiered,
                'season': season,
                'episode': episode,
                'ts': ts,
                'sources': sources_list,
                'id': film_id
            })

            url = urllib.urlencode(data)

            return url

        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):

        sources = []

        try:
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)
            data['sources'] = re.findall("[^', u\]\[]+", data['sources'])
            try:
                q = re.findall("\.(.*)", data['id'])[0]
            except:
                q = data['id']
            query = (self.tooltip_path % q)
            url = urlparse.urljoin(self.base_link, query)
            q = client.request(url)
            quality = re.findall('ty">(.*?)<', q)[0]
            if '1080p' in quality:
                quality = '1080p'
            elif '720p' in quality:
                quality = 'HD'
                        
            for i in data['sources']:
                token = str(self.__token(
                    {'id': i, 'server': 28, 'update': 0, 'ts': data['ts']}))
                query = (self.info_path % (data['ts'], token, i))
                url = urlparse.urljoin(self.base_link, query)
                info_response = client.request(url, XHR=True)
                grabber_dict = json.loads(info_response)

                try:
                    if grabber_dict['type'] == 'direct':
                        token64 = grabber_dict['params']['token']
                        query = (self.grabber_path % (data['ts'], i, token64))
                        url = urlparse.urljoin(self.base_link, query)

                        response = client.request(url, XHR=True)

                        sources_list = json.loads(response)['data']
                        
                        for j in sources_list:
                            
                            quality = j['label'] if not j['label'] == '' else 'SD'
                            #quality = 'HD' if quality in ['720p','1080p'] else 'SD'
                            quality = source_utils.label_to_quality(quality)

                            if 'googleapis' in j['file']:
                                sources.append({'source': 'GVIDEO', 'quality': quality, 'language': 'en', 'url': j['file'], 'direct': True, 'debridonly': False})
                                continue

                            #source = directstream.googlepass(j['file'])
                            valid, hoster = source_utils.is_host_valid(j['file'], hostDict)
                            urls, host, direct = source_utils.check_directstreams(j['file'], hoster)
                            for x in urls:
                                sources.append({
                                    'source': 'gvideo',
                                    'quality': quality,
                                    'language': 'en',
                                    'url': x['url'],
                                    'direct': True,
                                    'debridonly': False
                                })

                    elif not grabber_dict['target'] == '':
                        url = 'https:' + grabber_dict['target'] if not grabber_dict['target'].startswith('http') else grabber_dict['target']
                        #host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                        valid, hoster = source_utils.is_host_valid(url, hostDict)
                        if not valid: continue
                        urls, host, direct = source_utils.check_directstreams(url, hoster)
                        sources.append({
                            'source': hoster,
                            'quality': quality,
                            'language': 'en',
                            'url': urls[0]['url'], #url.replace('\/','/'),
                            'direct': False,
                            'debridonly': False
                        })
                except: pass
                    
            return sources

        except Exception:
            return sources

    def resolve(self, url):
        try:
            if not url.startswith('http'):
                url = 'http:' + url

            for i in range(3):
                if 'google' in url and not 'googleapis' in url:
                    url = directstream.googlepass(url)

                if url:
                    break

            return url

        except Exception:
            return

    def __token(self, r):
        
        def additup(t):
            n = 0
            for i in range(0, len(t)):
                n += ord(t[i]) + i
            return n

        try:
            base = "iQDWcsGqN"
            s = additup(base)
            for n in r:
                t = base + n
                i = str(r[n])
                e = 0
                for x in range(0,max(len(t), len(i))):
                    e += ord(i[x]) if x < len(i) else 0
                    e += ord(t[x]) if x < len(t) else 0
                s += additup(str(hex(e))[2:])
            return s

        except Exception:
            return 0