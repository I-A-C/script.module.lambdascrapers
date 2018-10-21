# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 10-10-2018 by JewBMX in Yoda.

import re
import urllib
import urlparse

from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import proxy


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['myputlocker.me','beetv.to']
		self.base_link = 'http://myputlocker.me'
		self.search_link = '/%s-s%s-e%s'

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except:
			return
 
	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url: return
			url = self.base_link + self.search_link % (url,season,episode)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			scraper = cfscrape.create_scraper()
			r = scraper.get(url).content
			try:
				match = re.compile("<iframe src='(.+?)://(.+?)/(.+?)'",re.DOTALL).findall(r)
				for http,host,url in match:
					url = '%s://%s/%s' % (http,host,url)
					sources.append({'source': host,'quality': 'SD','language': 'en','url': url,'direct': False,'debridonly': False}) 
			except:
				return
		except Exception:
			return
		return sources

	def resolve(self, url):
		return url