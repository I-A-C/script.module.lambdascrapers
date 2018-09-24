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

import re,traceback,urlparse,random,urllib

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import dom_parser2
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['icefilms.info','icefilms.unblocked.pro','icefilms.unblocked.vc','icefilms.unblocked.sh']
        self.base_url = 'http://icefilms.unblocked.sh'
        self.search_link = urlparse.urljoin(self.base_url, 'search.php?q=%s+%s&x=0&y=0')
        self.list_url = urlparse.urljoin(self.base_url, 'membersonly/components/com_iceplayer/video.php?h=374&w=631&vid=%s&img=')
        self.post = 'id=%s&s=%s&iqs=&url=&m=%s&cap= &sec=%s&t=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = self.search_link % (clean_title.replace('-','+'), year)
            headers = {'Host': 'http://icefilms1.unblocked.sh',
                       'Cache-Control': 'max-age=0',
                        'Connection': 'keep-alive',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                        'Upgrade-Insecure-Requests': '1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'en-US,en;q=0.8'}

            r = client.request(search_url, headers=headers)
            r = dom_parser2.parse_dom(r, 'td')
            r = [dom_parser2.parse_dom(i, 'a', req='href') for i in r if "<div class='number'" in i.content]
            r = [(urlparse.urljoin(self.base_url, i[0].attrs['href'])) for i in r if title.lower() in i[0].content.lower() and year in i[0].content]
            url = r[0]
            url = url[:-1]
            url = url.split('?v=')[1]
            url = self.list_url % url
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('IceFilms - Exception: \n' + str(failure))
            return
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(tvshowtitle)
            search_url = self.search_link % (clean_title.replace('-','+'), year)
            r = client.request(search_url, headers=self.headers)
            r = dom_parser2.parse_dom(r, 'td')
            r = [dom_parser2.parse_dom(i, 'a', req='href') for i in r if "<div class='number'" in i.content]
            r = [(urlparse.urljoin(self.base_url, i[0].attrs['href'])) for i in r if tvshowtitle.lower() in i[0].content.lower() and year in i[0].content]
            url = r[0]
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('IceFilms - Exception: \n' + str(failure))
            return
            
    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            sep = '%dx%02d' % (int(season), int(episode))
            r = client.request(url, headers=self.headers)
            r = dom_parser2.parse_dom(r, 'span', attrs={'class': 'list'})
            r1 = dom_parser2.parse_dom(r, 'br')
            r1 = [dom_parser2.parse_dom(i, 'a', req='href') for i in r1]
            try:
                if int(season) == 1 and int(episode) == 1:
                    url = dom_parser2.parse_dom(r, 'a', req='href')[1].attrs['href']
                else:
                    for i in r1:
                        if sep in i[0].content:
                            url = urlparse.urljoin(self.base_url, i[0].attrs['href'])
            except:
                pass
            url = url[:-1]
            url = url.split('?v=')[1]
            url = self.list_url % url
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('IceFilms - Exception: \n' + str(failure))
            return
            
    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []     
            url_for_post = url
            headers = {'Host': 'http://icefilms1.unblocked.lol',
                       'Connection': 'keep-alive',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                       'Upgrade-Insecure-Requests': '1',
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                       'Accept-Encoding': 'gzip, deflate, br',
                       'Accept-Language': 'en-US,en;q=0.8'}

            cookie = client.request(url, close=False, headers=headers, output='cookie')
            html = client.request(url, close=False, headers=headers, cookie=cookie)
            match = re.search('lastChild\.value="([^"]+)"(?:\s*\+\s*"([^"]+))?', html)
            secret = ''.join(match.groups(''))
            match = re.search('"&t=([^"]+)', html)
            t = match.group(1)
            
            match = re.search('(?:\s+|,)s\s*=(\d+)', html)
            s_start = int(match.group(1))
            
            match = re.search('(?:\s+|,)m\s*=(\d+)', html)
            m_start = int(match.group(1))
            
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
                    host = re.sub('(</?[^>]*>)', '', host_fragment)
                    info = []
                    
                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', host)[-1]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except:
                        pass

                    host = re.search('([a-zA-Z]+)', host)
                    host = host.group(1)
                    info = ' | '.join(info)

                    s = s_start + random.randint(3, 1000)
                    m = m_start + random.randint(21, 1000)
                    
                    post = self.post % (link_id, s, m, secret, t)

                    headers =  {'Host': 'http://icefilms1.unblocked.lol',
                                'Connection': 'keep-alive',
                                'Content-Length': '65',
                                'Origin': 'http://icefilms1.unblocked.lol',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                                'Content-type': 'application/x-www-form-urlencoded',
                                'Accept': '*/*',
                                'Referer': url_for_post,
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept-Language': 'en-US,en;q=0.8'}
                    url = urlparse.urljoin(self.base_url, 'membersonly/components/com_iceplayer/video.phpAjaxResp.php?s=%s&t=%s' % (link_id, t))
                    r = client.request(url, cookie=cookie, close=False, headers=headers, post=post)
                    match = re.search('url=(http.*)', r)
                    if match: 
                        if host.lower() in str(hostDict):
                            url = urllib.unquote_plus(match.group(1))
                            sources.append({
                                'source': host,
                                'info': info,
                                'quality': quality,
                                'language': 'en',
                                'url': url.replace('\/','/'),
                                'direct': False,
                                'debridonly': False
                            })
                        elif host.lower() in str(hostprDict):
                            url = urllib.unquote_plus(match.group(1))
                            sources.append({
                                'source': host,
                                'info': info,
                                'quality': quality,
                                'language': 'en',
                                'url': url.replace('\/','/'),
                                'direct': False,
                                'debridonly': True
                            })
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('IceFilms - Exception: \n' + str(failure))
            return
            
    def resolve(self, url):
        return url
