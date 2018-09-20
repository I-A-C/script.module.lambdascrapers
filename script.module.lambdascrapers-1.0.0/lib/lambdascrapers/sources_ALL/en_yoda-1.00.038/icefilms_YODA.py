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
# Addon Provider: Supremacy

import re,urlparse,random,urllib,time

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import dom_parser2
from resources.lib.modules import log_utils
from resources.lib.modules import cfscrape
from resources.lib.modules import workers

import requests
def url_ok(url):
    r = requests.head(url)
    if r.status_code == 200 or r.status_code == 301:
        return True
    else: return False

def HostChcker():
    if url_ok("https://ice.unblocked.lol"):
        useurl = 'https://ice.unblocked.lol/'
		
    elif url_ok("https://icefilms.unblocked.lat"):
        useurl = 'https://icefilms.unblocked.lat/'

    elif url_ok("http://www.icefilms.info"):
        useurl = 'http://www.icefilms.info/'


    else: useurl = 'http://localhost/'
    
    return useurl

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['icefilms.info','icefilms.unblocked.vc','www6-icefilms6-info.unblocked.lol']
        self.base_link = HostChcker()
        self.search_link = urlparse.urljoin(self.base_link, 'search.php?q=%s+%s&x=0&y=0')
        self.list_url = urlparse.urljoin(self.base_link, 'membersonly/components/com_iceplayer/video.php?h=374&w=631&vid=%s&img=')
        self.post = 'id=%s&s=%s&iqs=&url=&m=%s&cap= &sec=%s&t=%s'
                       
    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = self.search_link % (clean_title.replace('-','+'), year)
            self.scraper = cfscrape.create_scraper()
            r = self.scraper.get(search_url).content
            if 'To proceed, you must allow popups' in r:
                for i in range(0, 5):
                    r = self.scraper.get(search_url).content
                    if 'To proceed, you must allow popups' not in r: break  
            r = dom_parser2.parse_dom(r, 'div', attrs={'class':'title'})

            r = [dom_parser2.parse_dom(i, 'a', req='href') for i in r]
            r = [(urlparse.urljoin(self.base_link, i[0].attrs['href'])) for i in r if title.lower() in i[0].content.lower() and year in i[0].content]
            url = r[0]
            url = url[:-1]
            url = url.split('?v=')[1]
            url = self.list_url % url
            return url
        except Exception:
            return
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(tvshowtitle)
            search_url = self.search_link % (clean_title.replace('-','+'), year)
            self.scraper = cfscrape.create_scraper()
            r = self.scraper.get(search_url).content

            if 'To proceed, you must allow popups' in r:
                for i in range(0, 5):
                    r = self.scraper.get(search_url).content
                    if 'To proceed, you must allow popups' not in r: break
            r = dom_parser2.parse_dom(r, 'div', attrs={'class': 'title'})

            r = [dom_parser2.parse_dom(i, 'a', req='href') for i in r]
            r = [(urlparse.urljoin(self.base_link, i[0].attrs['href'])) for i in r if tvshowtitle.lower() in i[0].content.lower() and year in i[0].content]
            url = r[0]
            return url
        except:
            return
            
    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            sep = '%dx%02d' % (int(season), int(episode))
            r = self.scraper.get(url).content
            if 'To proceed, you must allow popups' in r:
                for i in range(0, 5):
                    r = self.scraper.get(url).content
                    if 'To proceed, you must allow popups' not in r: break    
            r = dom_parser2.parse_dom(r, 'span', attrs={'class': 'list'})
            r1 = dom_parser2.parse_dom(r, 'br')
            r1 = [dom_parser2.parse_dom(i, 'a', req='href') for i in r1]
            try:
                if int(season) == 1 and int(episode) == 1:
                    url = dom_parser2.parse_dom(r, 'a', req='href')[1].attrs['href']
                else:
                    for i in r1:
                        if sep in i[0].content:
                            url = urlparse.urljoin(self.base_link, i[0].attrs['href'])
            except:
                pass
            url = url[:-1]
            url = url.split('?v=')[1]
            url = self.list_url % url
            return url
        except:
            return
            
    def sources(self, url, hostDict, hostprDict):
    
        self._sources = []
        try:                
            if not url: return self._sources
            
            self.hostDict = hostDict
            self.hostprDict = hostprDict
   
            referer = url
            
            html = self.scraper.get(url).content
            if 'To proceed, you must allow popups' in html:
                for i in range(0, 5):
                    html = self.scraper.get(url).content
                    if 'To proceed, you must allow popups' not in html: break
            match = re.search('lastChild\.value="([^"]+)"(?:\s*\+\s*"([^"]+))?', html)
            
            secret = ''.join(match.groups(''))
            match = re.search('"&t=([^"]+)', html)
            t = match.group(1)
            match = re.search('(?:\s+|,)s\s*=(\d+)', html)
            s_start = int(match.group(1))
            
            match = re.search('(?:\s+|,)m\s*=(\d+)', html)
            m_start = int(match.group(1))
            
            threads = []
            
            for fragment in dom_parser2.parse_dom(html, 'div', {'class': 'ripdiv'}):
                match = re.match('<b>(.*?)</b>', fragment.content)
                if match:
                    q_str = match.group(1).replace(' ', '').upper()
                    if '1080' in q_str: quality = '1080p'
                    elif '720' in q_str: quality = '720p'
                    elif '4k' in q_str.lower(): quality = '4K'
                    else: quality = 'SD'
                else:
                    quality = 'SD'
                                
                pattern = '''onclick='go\((\d+)\)'>([^<]+)(<span.*?)</a>'''
                for match in re.finditer(pattern, fragment.content):
                    link_id, label, host_fragment = match.groups()
                    s = s_start + random.randint(3, 1000)
                    m = m_start + random.randint(21, 1000)                            
                    post = self.post % (link_id, s, m, secret, t)
                    url = urlparse.urljoin(self.base_link, 'membersonly/components/com_iceplayer/video.phpAjaxResp.php?s=%s&t=%s' % (link_id, t))
                                        
                    threads.append(workers.Thread(self._get_sources, url, post, host_fragment, quality, referer))
            
            [i.start() for i in threads]
            [i.join() for i in threads]

            alive = [x for x in threads if x.is_alive() == True]
            while alive:
                alive = [x for x in threads if x.is_alive() == True]
                time.sleep(0.1)
            return self._sources
        except:
            return self._sources
            
    def _get_sources(self, url, post, host_fragment, quality, referer):
        try:
            url = {'link': url, 'post': post, 'referer': referer}
            url = urllib.urlencode(url)

            valid = True
            host_size = re.sub('(</?[^>]*>)', '', host_fragment)
            host = re.search('([a-zA-Z]+)', host_size)
            host = host.group(1)
            if host.lower() in str(self.hostDict): debrid_only = False
            elif host.lower() in str(self.hostprDict): debrid_only = True
            else: valid = False
            
            if valid:
                info = []
                
                try:
                    size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', host_size)[-1]
                    div = 1 if size.endswith(('GB', 'GiB')) else 1024
                    size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                    size = '%.2f GB' % size
                    info.append(size)
                except:
                    pass

                info = ' | '.join(info)
                self._sources.append({
                    'source': host,
                    'info': info,
                    'quality': quality,
                    'language': 'en',
                    'url': url,
                    'direct': False,
                    'debridonly': debrid_only
                })
        except:
            pass

    def resolve(self, url):
        try:
            scraper = cfscrape.create_scraper()
            data_dict = urlparse.parse_qs(url)
            data_dict = dict([(i, data_dict[i][0]) if data_dict[i] else (i, '') for i in data_dict])
            link = data_dict['link']
            post = data_dict['post']
            referer = data_dict['referer']
            for i in range(0, 5):
                scraper.get(referer).content
                getheaders =  {'Host': 'icefilms.unblocked.vc',
                                'Origin': 'https://icefilms.unblocked.vc',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                                'Content-type': 'application/x-www-form-urlencoded',
                                'Referer': referer}
                r = scraper.post(link, data=post, headers=getheaders).text
                match = re.search('url=(http.*)', r)
                if match: 
                    return urllib.unquote_plus(match.group(1))
            return
        except:
            return