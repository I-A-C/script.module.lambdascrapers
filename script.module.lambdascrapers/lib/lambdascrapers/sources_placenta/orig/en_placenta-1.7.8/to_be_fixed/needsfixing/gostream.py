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


import re,urllib,urlparse,time,json

from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import jsunpack
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['gostream.is','gomovies.to','gomovies.sc']
        self.base_link = 'https://www3.gomovies.sc/'
        self.search_link = '/searching-for/%s/'
        self.user = control.setting('gostream.user')
        self.password = control.setting('gostream.pass')

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
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


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            if (self.user != '' and self.password != ''): #raise Exception()

               login = urlparse.urljoin(self.base_link, '/login.html')

               post = urllib.urlencode({'username': self.user, 'password': self.password, 'submit': 'Login'})

               cookie = client.request(login, post=post, output='cookie', close=False)

               r = client.request(login, post=post, cookie=cookie, output='extended')

               headers = {'User-Agent': r[3]['User-Agent'], 'Cookie': r[4]}
            else:
               headers = {}


            if not str(url).startswith('http'):

                data = urlparse.parse_qs(url)
                data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

                title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
                if 'season' in data: season = data['season']
                if 'episode' in data: episode = data['episode']
                year = data['year']

                query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(title)))
                query2 = urlparse.urljoin(self.base_link, self.search_link % re.sub('\s','+',title))
                r = client.request(query)
                r = client.parseDOM(r, 'div', attrs = {'class': 'ml-item'})
                if len(r)==0:
                    r = client.request(query2)
                    r = client.parseDOM(r, 'div', attrs = {'class': 'ml-item'})
                r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'), client.parseDOM(r, 'a', ret='data-url'))
                
                if 'tvshowtitle' in data:                   
                    cltitle = cleantitle.get(title+'season'+season)
                    cltitle2 = cleantitle.get(title+'season%02d'%int(season))
                else:
                    cltitle = cleantitle.get(title)

                r = [i for i in r if cltitle == cleantitle.get(i[1]) or cltitle2 == cleantitle.get(i[1])]
                id = [re.findall('/(\d+)$',i[2])[0] for i in r][0]

                ajx = urlparse.urljoin(self.base_link, '/ajax/movie_episodes/'+id)

                r = client.request(ajx)
                if 'episode' in data:
                    eids = re.findall(r'title=\\"Episode\s+%02d.*?data-id=\\"(\d+)'%int(episode),r)
                else:
                    eids = re.findall(r'title=.*?data-id=\\"(\d+)',r)

                for eid in eids:
                    try:
                        ajx = 'ajax/movie_token?eid=%s&mid=%s&_=%d' % (eid, id, int(time.time() * 1000))
                        ajx = urlparse.urljoin(self.base_link, ajx)
                        r = client.request(ajx)
                        [x,y] = re.findall(r"_x='([^']+)',\s*_y='([^']+)'",r)[0]
                        ajx = 'ajax/movie_sources/%s?x=%s&y=%s'%(eid,x,y)
                        ajx = urlparse.urljoin(self.base_link, ajx)
                        r = client.request(ajx)
                        r = json.loads(r)
                        r = r['playlist'][0]['sources']
                        for i in r:
                            try: label = source_utils.label_to_quality(i['label']) 
                            except: label = 'SD'
                            sources.append({'source': 'cdn', 'quality': label, 'language': 'en', 'url': i['file'], 'direct': True, 'debridonly': False})
                    except:
                        pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


