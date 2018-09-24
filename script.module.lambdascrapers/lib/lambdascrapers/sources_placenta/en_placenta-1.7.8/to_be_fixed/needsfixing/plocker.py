# -*- coding: UTF-8 -*-
# ######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
# ######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo

import re,traceback,urllib,urlparse,json,random, time

from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import directstream
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['putlocker.se','putlockertv.to']
        self.base_link = 'https://www2.putlockertv.to/'
        self.movie_search_path = ('search?keyword=%s')
        self.film_path = '/watch/%s'
        self.info_path = '/ajax/episode/info?ts=%s&_=%s&id=%s&server=28&update=0'
        self.grabber_path = '/grabber-api/?ts=%s&id=%s&token=%s&mobile=0'
        self.tooltip_path = '/ajax/film/tooltip/%s'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_title = cleantitle.getsearch(title).replace(' ','+')
            query = (self.movie_search_path % (clean_title))
            url = urlparse.urljoin(self.base_link, query)
            for r in range(1,3):
                search_response = client.request(url)
                if search_response != None: break
            results_list = client.parseDOM(search_response, 'div', attrs={'class': 'item'})            
            for result in results_list:
                tip = client.parseDOM(result, 'div', attrs={'class':'inner'}, ret='data-tip')[0]
                url = urlparse.urljoin(self.base_link, tip)
                tip_response = client.request(url, timeout=10)
                if year in tip_response:
                    film_id = re.findall('(\/watch\/)([^\"]*)', results_list)[0][1]
                    break
            query = (self.film_path % film_id)
            url = urlparse.urljoin(self.base_link, query)
            self.film_url = url
            for r in range(1,3):
                film_response = client.request(url, timeout=10)
                if film_response != None: break
            ts = re.findall('(data-ts=\")(.*?)(\">)', film_response)[0][1]
            server_ids = client.parseDOM(film_response, 'div', ret='data-id', attrs={'class': 'server row'})
            sources_dom_list = client.parseDOM(
                film_response, 'ul', attrs={'class': 'episodes range active'})
            sources_list = []
            for i in sources_dom_list:
                source_id = re.findall('([\/])(.{0,6})(\">)', i)[0][1]
                sources_list.append(source_id)
            sources_list = zip(sources_list, server_ids)
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
        except:
            failure = traceback.format_exc()
            log_utils.log('PLocker - Exception: \n' + str(failure))
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
        except:
            failure = traceback.format_exc()
            log_utils.log('PLocker - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)
            clean_title = cleantitle.geturl(data['tvshowtitle'])
            query = (self.movie_search_path % clean_title)
            url = urlparse.urljoin(self.base_link, query)
            for r in range(1,3):
                search_response = client.request(url, timeout=10)
                if search_response != None: break
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
            self.film_url = url
            for r in range(1,3):
                film_response = client.request(url, timeout=10)
                if film_response != None: break
            ts = re.findall('(data-ts=\")(.*?)(\">)', film_response)[0][1]
            server_ids = client.parseDOM(film_response, 'div', ret='data-id', attrs={'class': 'server row'})
            sources_dom_list = client.parseDOM(film_response, 'ul', attrs={'class': 'episodes range active'})
            if not re.findall(
             '([^\/]*)\">' + episode + '[^0-9]', sources_dom_list[0]):
                episode = '%02d' % int(episode)
            sources_list = []
            for i in sources_dom_list:
                try:
                    source_id = re.findall(('([^\/]*)\">' + episode + '[^0-9]'), i)[0]
                    sources_list.append(source_id)
                except:
                    pass
            sources_list = zip(sources_list, server_ids)
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
        except:
            failure = traceback.format_exc()
            log_utils.log('PLocker - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            data = urlparse.parse (url)
            data = dict((i, data[i][0]) if data[i] else (i, '') for i in data)
            data['sources'] = re.findall("[^', u\]\[]+", data['sources'])
            for i,s in data['sources']:
                token = str(self.__token(
                    {'id': i, 'server': 28, 'update': 0, 'ts': data['ts']}, 'iQDWcsGqN'))
                query = (self.info_path % (data['ts'], token, i, s))
                url = urlparse.urljoin(self.base_link, query)
                for r in range(1,3):
                    info_response = client.request(url, XHR=True, timeout=10)
                    if info_response != None: break
                grabber_dict = json.loads(info_response)
                try:
                    if grabber_dict['type'] == 'direct':
                        token64 = grabber_dict['params']['token']
                        randint = random.randint(1000000,2000000)
                        query = (self.grabber_path % (data['ts'], i, token64))
                        url = urlparse.urljoin(self.base_link, query)
                        for r in range(1,3):
                            response = client.request(url, XHR=True, timeout=10)
                            if response != None: break
                        sources_list = json.loads(response)['data']
                        for j in sources_list:
                            quality = j['label'] if not j['label'] == '' else 'SD'
                            quality = source_utils.label_to_quality(quality)
                            urls = None
                            if 'googleapis' in j['file']:
                                sources.append({'source': 'GVIDEO', 'quality': quality, 'language': 'en', 'url': j['file'], 'direct': True, 'debridonly': False})
                                continue
                            if 'lh3.googleusercontent' in j['file'] or 'bp.blogspot' in j['file']:
                                try:
                                    newheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                                           'Accept': '*/*',
                                           'Host': 'lh3.googleusercontent.com',
                                           'Accept-Language': 'en-US,en;q=0.8,de;q=0.6,es;q=0.4',
                                           'Accept-Encoding': 'identity;q=1, *;q=0',
                                           'Referer': self.film_url,
                                           'Connection': 'Keep-Alive',
                                           'X-Client-Data': 'CJK2yQEIo7bJAQjEtskBCPqcygEIqZ3KAQjSncoBCKijygE=',
                                           'Range': 'bytes=0-'
                                      }
                                    resp = client.request(j['file'], headers=newheaders, redirect=False, output='extended', timeout='10')
                                    loc = resp[2]['Location']
                                    c = resp[2]['Set-Cookie'].split(';')[0]
                                    j['file'] = '%s|Cookie=%s' % (loc, c)
                                    urls, host, direct = [{'quality': quality, 'url': j['file']}], 'gvideo', True    
                                except: 
                                    pass
                            valid, hoster = source_utils.is_host_valid(j['file'], hostDict)
                            if not urls or urls == []:
                                urls, host, direct = source_utils.check_directstreams(j['file'], hoster)
                            for x in urls:
                                sources.append({'source': 'gvideo', 'quality': x['quality'], 'language': 'en', 'url': x['url'],
                                 'direct': True, 'debridonly': False})
                    elif not grabber_dict['target'] == '':
                        url = 'https:' + grabber_dict['target'] if not grabber_dict['target'].startswith('http') else grabber_dict['target']
                        valid, hoster = source_utils.is_host_valid(url, hostDict)
                        if not valid: continue
                        urls, host, direct = source_utils.check_directstreams(url, hoster)
                        sources.append({'source': hoster, 'quality': urls[0]['quality'], 'language': 'en', 'url': urls[0]['url'], 
                            'direct': False, 'debridonly': False})
                except: pass
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('PLocker - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        try:
            #if 'mcloud' in url:
             #   url = client.request(url)
             #   url = re.findall('''file['"]:['"]([^'"]+)['"]''', url, re.DOTALL)[0]
            if not url.startswith('http'):
                url = 'http:' + url
            for i in range(3):
                if 'google' in url and not 'googleapis' in url:
                    url = directstream.googlepass(url)
                if url:
                    break
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('PLocker - Exception: \n' + str(failure))
            return
        
    def ___token(self, params, It):
        try:
            def r(t):
                i = 0
                j = 0
                for i in range (0, len(t)):
                    j = j + (ord(t[i]) +i)
                return j
            s = r(It)            
            for p in params:
                t = It + p
                i = str(params[p])
                l = max(len(t), len(i))
                e = 0
                for n in range(0, l):            
                    if n < len(i):
                        e += ord(i[n])
                    if n < len(t):
                        e += ord(t[n])
                e = str(hex(e)).replace('0x','')
                e = r(e)
                s += e
            return s
        except Exception:
            return 0   
        
    def __token(self, d):
        try:
            token = 0
            for s in d:
                o = 0
                r = 0
                i = [i for i in range(0, 256)]
                n = 0
                a = 0
                j = s
                e = str(d[s])
                for t in range(0, 256):
                    n = (n + i[t] + ord(j[t % len(j)])) % 256
                    r = i[t]
                    i[t] = i[n]
                    i[n] = r
                s = 0
                n = 0
                for o in range(len(e)):
                    s = (s + 1) % 256
                    n = (n + i[s]) % 256
                    r = i[s]
                    i[s] = i[n]
                    i[n] = r
                    a += ord(e[o]) ^ i[(i[s] + i[n]) % 256] * o + o
                token += a
            return token
        except Exception:
            return 0