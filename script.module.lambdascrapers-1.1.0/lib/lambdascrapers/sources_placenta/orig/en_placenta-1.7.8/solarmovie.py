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


import re,traceback,urllib,urlparse,hashlib,random,string,json,base64,sys,xbmc,resolveurl

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils
from resources.lib.modules import cache
from resources.lib.modules import directstream
from resources.lib.modules import jsunfuck


CODE = '''def retA():
    class Infix:
        def __init__(self, function):
            self.function = function
        def __ror__(self, other):
            return Infix(lambda x, self=self, other=other: self.function(other, x))
        def __or__(self, other):
            return self.function(other)
        def __rlshift__(self, other):
            return Infix(lambda x, self=self, other=other: self.function(other, x))
        def __rshift__(self, other):
            return self.function(other)
        def __call__(self, value1, value2):
            return self.function(value1, value2)
    def my_add(x, y):
        try: return x + y
        except Exception: return str(x) + str(y)
    x = Infix(my_add)
    return %s
param = retA()'''


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']

        self.domains = ['solarmovie.ms']
        self.base_link = 'http://www.solarmovie.ms'
        self.search_link = '/keywords/%s'
		# Testing: Star Wars: Episode II - Attack Of The Clones
		# Failed:  http://www.solarmovie.ms/keywords/star%20wars%20%20episode%20ii%20%20%20attack%20of%20the%20clones
        # Working: http://www.solarmovie.ms/keywords/Star%20Wars:%20Episode%20II%20-%20Attack%20Of%20The%20Clones
		# Changing ANY punctuation or spaces results in failure!!! (different case is fine)
		# http://www.solarmovie.ms/watch-star-wars-episode-ii-attack-of-the-clones-online.html

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
#           search_id = title.lower().replace(':', ' ').replace('-', ' ') # see __init__

#           start_url = urlparse.urljoin(self.base_link, (self.search_link % (search_id.replace(' ','%20'))))         
            start_url = urlparse.urljoin(self.base_link, (self.search_link % (title.replace(' ','%20'))))  
            
            headers={'User-Agent':client.randomagent()}
            html = client.request(start_url,headers=headers)    		
            
            match = re.compile('<span class="name"><a title="(.+?)" href="(.+?)".+?title="(.+?)"',re.DOTALL).findall(html)
            for name,item_url, link_year in match:
                if year in link_year:                                                        
                    if cleantitle.get(title) in cleantitle.get(name):
                        return item_url
            return
        except:
            failure = traceback.format_exc()
            log_utils.log('SolarMovie - Exception: \n' + str(failure))

        self.domains = ['solarmoviez.to', 'solarmoviez.ru']
        self.base_link = 'https://solarmoviez.ru'
        self.search_link = '/movie/search/%s.html'
        self.info_link = '/ajax/movie_info/%s.html?is_login=false'
        self.server_link = '/ajax/v4_movie_episodes/%s'
        self.embed_link = '/ajax/movie_embed/%s'
        self.token_link = '/ajax/movie_token?eid=%s&mid=%s'
        self.source_link = '/ajax/movie_sources/%s?x=%s&y=%s'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def searchShow(self, title, season, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            search = '%s Season %s' % (title, season)
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(search)))

            r = client.request(url)

            url = re.findall('<a href=\"(.+?\/movie\/%s-season-%s-.+?\.html)\"' % (cleantitle.geturl(title), season), r)[0]

            return url

        except:
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(title)))
            r = client.request(url, headers=headers, timeout='15')
            r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            results = [(i[0], i[1], re.findall('\((\d{4})', i[1])) for i in r]
            try:
                r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
                url = [i[0] for i in r if self.matchAlias(i[1], aliases) and (year == i[2])][0]
            except:
                url = None
                pass

            if (url == None):
                url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]
            return url
        except:

            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources


            headers={'User-Agent':client.randomagent()}
            html = client.request(url,headers=headers)

            Links = re.compile('id="link_.+?target="_blank" id="(.+?)"',re.DOTALL).findall(html)
            for vid_url in Links:
                if 'openload' in vid_url:
                    try:
                        source_html   = client.request(vid_url,headers=headers)
                        source_string = re.compile('description" content="(.+?)"',re.DOTALL).findall(source_html)[0]
                        quality,info = source_utils.get_release_quality(source_string, vid_url)
                    except:
                        quality = 'DVD'
                        info = []
                    sources.append({'source': 'Openload','quality': quality,'language': 'en','url':vid_url,'info':info,'direct': False,'debridonly': False})
                elif 'streamango' in vid_url:
                    try:  
                        source_html = client.request(vid_url,headers=headers)
                        source_string = re.compile('description" content="(.+?)"',re.DOTALL).findall(source_html)[0]
                        quality,info = source_utils.get_release_quality(source_string, vid_url)  
                    except:
                        quality = 'DVD'
                        info = []
                    sources.append({'source': 'Streamango','quality': quality,'language': 'en','url':vid_url,'info':info,'direct': False,'debridonly': False})
                else:
                    if resolveurl.HostedMediaFile(vid_url):
                        quality,info = source_utils.get_release_quality(vid_url, vid_url)  
                        host = vid_url.split('//')[1].replace('www.','')
                        host = host.split('/')[0].split('.')[0].title()
                        sources.append({'source': host,'quality': quality,'language': 'en','url':vid_url,'info':info,'direct': False,'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('SolarMovie - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                episode = int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)
            else:
                episode = 0
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            mid = re.findall('-(\d+)', url)[-1]

            try:
                headers = {'Referer': url}
                u = urlparse.urljoin(self.base_link, self.server_link % mid)
                r = client.request(u, headers=headers, XHR=True)
                r = json.loads(r)['html']
                r = client.parseDOM(r, 'div', attrs = {'class': 'pas-list'})

                ids = client.parseDOM(r, 'li', ret='data-id')
                servers = client.parseDOM(r, 'li', ret='data-server')
                labels = client.parseDOM(r, 'a', ret='title')
                r = zip(ids, servers, labels)

                for eid in r:
                    try:
                        try:
                            ep = re.findall('episode.*?(\d+).*?', eid[2].lower())[0]
                        except:
                            ep = 0
                        if (episode == 0) or (int(ep) == episode):
                            url = urlparse.urljoin(self.base_link, self.token_link % (eid[0], mid))
                            script = client.request(url)
                            if '$_$' in script:
                                params = self.uncensored1(script)
                            elif script.startswith('[]') and script.endswith('()'):
                                params = self.uncensored2(script)
                            elif '_x=' in script:
                                x = re.search('''_x=['"]([^"']+)''', script).group(1)
                                y = re.search('''_y=['"]([^"']+)''', script).group(1)
                                params = {'x': x, 'y': y}
                            else:
                                raise Exception()

                            u = urlparse.urljoin(self.base_link, self.source_link % (eid[0], params['x'], params['y']))
                            r = client.request(u, XHR=True)
                            json_sources = json.loads(r)['playlist'][0]['sources']

                            try:
                                if 'google' in json_sources['file']:
                                    quality = 'HD'

                                    if 'bluray' in json_sources['file'].lower():
                                        quality = '1080p'

                                    sources.append({'source': 'gvideo', 'quality': quality, 'language': 'en',
                                                    'url': json_sources['file'], 'direct': True, 'debridonly': False})

                            except Exception:
                                if 'blogspot' in json_sources[0]['file']:
                                    url = [i['file'] for i in json_sources if 'file' in i]
                                    url = [directstream.googletag(i) for i in url]
                                    url = [i[0] for i in url if i]

                                    for s in url:
                                        sources.append({'source': 'gvideo', 'quality': s['quality'], 'language': 'en',
                                                        'url': s['url'], 'direct': True, 'debridonly': False})

                                elif 'lemonstream' in json_sources[0]['file']:
                                    sources.append({
                                        'source': 'CDN',
                                        'quality': 'HD',
                                        'language': 'en',
                                        'url': json_sources[0]['file'] + '|Referer=' + self.base_link,
                                        'direct': True,
                                        'debridonly': False})
                    except:
                        pass
            except:
                pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def uncensored(a, b):
        x = '' ; i = 0
        for i, y in enumerate(a):
            z = b[i % len(b) - 1]
            y = int(ord(str(y)[0])) + int(ord(str(z)[0]))
            x += chr(y)
        x = base64.b64encode(x)
        return x

    def uncensored1(self, script):
        try:
            script = '(' + script.split("(_$$)) ('_');")[0].split("/* `$$` */")[-1].strip()
            script = script.replace('(__$)[$$$]', '\'"\'')
            script = script.replace('(__$)[_$]', '"\\\\"')
            script = script.replace('(o^_^o)', '3')
            script = script.replace('(c^_^o)', '0')
            script = script.replace('(_$$)', '1')
            script = script.replace('($$_)', '4')

            vGlobals = {"__builtins__": None, '__name__': __name__, 'str': str, 'Exception': Exception}
            vLocals = {'param': None}
            exec (CODE % script.replace('+', '|x|'), vGlobals, vLocals)
            data = vLocals['param'].decode('string_escape')
            x = re.search('''_x=['"]([^"']+)''', data).group(1)
            y = re.search('''_y=['"]([^"']+)''', data).group(1)
            return {'x': x, 'y': y}
        except:
            pass

    def uncensored2(self, script):
        try:
            js = jsunfuck.JSUnfuck(script).decode()
            x = re.search('''_x=['"]([^"']+)''', js).group(1)
            y = re.search('''_y=['"]([^"']+)''', js).group(1)
            return {'x': x, 'y': y}
        except:
            pass

