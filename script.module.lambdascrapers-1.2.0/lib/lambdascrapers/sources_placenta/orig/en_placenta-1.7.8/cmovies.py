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


import re,base64, requests, sys, urllib
from resources.lib.modules import jsunpack
from resources.lib.modules import cleantitle
from bs4 import BeautifulSoup

from resources.lib.modules import cfscrape

def streamdor(html, src, olod):
    source = ''
    try:
        with requests.Session() as s:
            episodeId = re.findall('.*streamdor.co/video/(\d+)', html)[0]
            p = s.get('https://embed.streamdor.co/video/' + episodeId, headers={'referer': src})
            p = re.findall(r'JuicyCodes.Run\(([^\)]+)', p.text, re.IGNORECASE)[0]
            p = re.sub(r'\"\s*\+\s*\"', '', p)
            p = re.sub(r'[^A-Za-z0-9+\\/=]', '', p)
            p = base64.b64decode(p)
            p = jsunpack.unpack(p.decode('utf-8'))
            qual = 'SD'
            try:
                qual = re.findall(r'label:"(.*?)"', p)[0]
            except:
                pass
            try:
                url = re.findall(r'(https://streamango.com/embed/.*?)"', p, re.IGNORECASE)[0]
                source = "streamango.com"
                details = {'source': source, 'quality': qual, 'language': "en", 'url': url, 'info': '',
                           'direct': False, 'debridonly': False}
            except:
                if olod == True:
                    url = ''
                    source = 'openload.co'
                    details = {'source': source, 'quality': qual, 'language': "en", 'url': url, 'info': '',
                               'direct': False, 'debridonly': False}
                else: return ''


        return details
    except:
        print("Unexpected error in CMOVIES STREAMDOR Script:")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        return details


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cmovieshd.io']
        self.base_link = 'https://www3.cmovies.io/'
        self.tv_link = 'https://www3.cmovies.io/tv-series/'
        self.movie_link = 'https://www3.cmovies.io/movie/'
        self.search_link = 'https://www3.cmovies.io/search/?q='

    def movie(self, imdb, title, localtitle, aliases, year):
        url = []
        sources = []
        with requests.Session() as s:
            p = s.get(self.search_link + title + "+" + year)
            soup = BeautifulSoup(p.text, 'html.parser').find_all('div', {'class':'movies-list'})[0]
            soup = soup.find_all('a', {'class':'ml-mask'})
            movie_link = ''
            for i in soup:
                if i['title'].lower() == title.lower() or i['title'].lower() == title.lower() + " " + year:
                    movie_link = i['href']
            p = s.get(movie_link +"watch")
            soup = BeautifulSoup(p.text, 'html.parser').find_all('a', {'class': 'btn-eps'})
            movie_links = []
            for i in soup:
                movie_links.append(i['href'])
            for i in movie_links:
                p = s.get(i)
                if re.findall(r'http.+://openload.co/embed/.+\"', p.text):
                    openload_link = re.findall(r'http.+://openload.co/embed/.+\"', p.text)[0].strip('"')
                    olo_source = streamdor(p.text, i, True)
                    olo_source['url'] = openload_link
                    sources.append(olo_source)

                else:
                    sources.append(streamdor(p.text, i, False))
            return sources

        return sources

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'tvshowtitle':tvshowtitle, 'aliases':aliases}
            return url
        except:
            print("Unexpected error in CMOVIES TV Script:")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if not url:
            return url
        try:

            aliases = url['aliases']
            aliases.append({'title':url['tvshowtitle']})
            sources = []
            if len(episode) == 1:
                episode = "0" + episode
            with requests.Session() as s:
                for i in aliases:
                    search_text = i['title'] + ' season ' + season
                    p = s.get(self.search_link + search_text)
                    soup = BeautifulSoup(p.text, 'html.parser')
                    soup = soup.find_all('div', {'class': 'ml-item'})[0].find_all('a', href=True)[0]
                    if re.sub(r'\W+', '', soup['title'].lower()) \
                            == re.sub(r'\W+', '', ((i['title'] + " - season " + season).lower())):
                        break
                    else:
                        soup = None
                        pass
                if soup == None:
                    return sources
            p = s.get(soup['href'] + 'watch')
            soup = BeautifulSoup(p.text, 'html.parser').find_all('a', {'class': 'btn-eps'})
            episode_links = []
            for i in soup:
                if re.sub(r'\W+','',title.lower()) in re.sub(r'\W+', '', i.text.lower()):
                    episode_links.append(i['href'])
            for i in episode_links:
                p = s.get(i)
                if re.findall(r'http.+://openload.co/embed/.+\"', p.text):
                    openload_link = re.findall(r'http.+://openload.co/embed/.+\"', p.text)[0].strip('"')
                    olo_source = streamdor(p.text, i, True)
                    olo_source['url'] = openload_link
                    sources.append(olo_source)

                else:
                    sources.append(streamdor(p.text, i, False))
            return sources

        except:
            print("Unexpected error in CMOVIES EPISODE Script:")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return sources


    def sources(self, url, hostDict, hostprDict):
        url = filter(None, url)
        sources = url
        return sources


    def resolve(self, url):
        return url

#url = source.tvshow(source(), '', '', 'Vikings','',[],'2016')
#uurl = source.episode(source(),url,'', '', 'A Good Treason', '', '4', '1')
#url = source.sources(source(),url,'','')