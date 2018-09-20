# -*- coding: UTF-8 -*-
#           ________
#          _,.-Y  |  |  Y-._
#      .-~"   ||  |  |  |   "-.
#      I" ""=="|" !""! "|"[]""|     _____
#      L__  [] |..------|:   _[----I" .-{"-.
#     I___|  ..| l______|l_ [__L]_[I_/r(=}=-P
#    [L______L_[________]______j~  '-=c_]/=-^
#     \_I_j.--.\==I|I==_/.--L_]
#       [_((==)[`-----"](==)j
#          I--I"~~"""~~"I--I
#          |[]|         |[]|
#          l__j         l__j
#         |!!|         |!!|
#          |..|         |..|
#          ([])         ([])
#          ]--[         ]--[
#          [_L]         [_L]
#         /|..|\       /|..|\
#        `=}--{='     `=}--{='
#       .-^--r-^-.   .-^--r-^-.
# Resistance is futile @lock_down... 
import scraper
import xbmcaddon
import xbmc
import os
import base64
import time
from salts_lib import pyaes
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES

BASE_URL = 'http://shush.se'
PY_URL = 'http://omaha.watchkodi.com/shush_scraper.dat'
KEY = base64.decodestring('YV9sb25nX2Flc19rZXlfZm9yX3NodXNoX3NjcmFwZXI=')
IV = '\0' * 16

class Shush_Proxy(scraper.Scraper):
    base_url = BASE_URL
    
    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.__update_scraper_py()
        try:
            import shush_scraper
            self.__scraper = shush_scraper.Shush_Scraper(timeout)
        except Exception as e:
            log_utils.log('Failure during shush scraper creation: %s' % (e), xbmc.LOGWARNING)
            self.__scraper = None
   
    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])
    
    @classmethod
    def get_name(cls):
        return 'Shush.se'
    
    def resolve_link(self, link):
        if self.__scraper is not None:
            return self.__scraper.resolve_link(link)
    
    def format_source_label(self, item):
        if self.__scraper is not None:
            return self.__scraper.format_source_label(item)
    
    def get_sources(self, video):
        if self.__scraper is not None:
            return self.__scraper.get_sources(video)
            
    def get_url(self, video):
        if self.__scraper is not None:
            return self.__scraper.get_url(video)
    
    def search(self, video_type, title, year):
        if self.__scraper is not None:
            return self.__scraper.search(video_type, title, year)
        else:
            return []
    
    def _get_episode_url(self, show_url, video):
        if self.__scraper is not None:
            return self.__scraper._get_episode_url(show_url, video)

    def _http_get(self, url, cache_limit=8):
        return super(Shush_Proxy, self)._cached_http_get(url, '', self.timeout, cache_limit=cache_limit)
    
    def __update_scraper_py(self):
        try:
            path = xbmcaddon.Addon().getAddonInfo('path')
            py_path = os.path.join(path, 'scrapers', 'shush_scraper.py')
            exists = os.path.exists(py_path)
            if  not exists or (exists and os.path.getmtime(py_path) < time.time() - (4 * 60 * 60)):
                cipher_text = self._http_get(PY_URL, cache_limit=4)
                if cipher_text:
                    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(KEY, IV))
                    new_py = decrypter.feed(cipher_text)
                    new_py += decrypter.feed()
                    
                    old_py = ''
                    if os.path.exists(py_path):
                        with open(py_path, 'r') as f:
                            old_py = f.read()
                    
                    log_utils.log('shush path: %s, new_py: %s, match: %s' % (py_path, bool(new_py), new_py == old_py), xbmc.LOGDEBUG)
                    if old_py != new_py:
                        with open(py_path, 'w') as f:
                            f.write(new_py)
        except Exception as e:
            log_utils.log('Failure during shush scraper update: %s' % (e), xbmc.LOGWARNING)
