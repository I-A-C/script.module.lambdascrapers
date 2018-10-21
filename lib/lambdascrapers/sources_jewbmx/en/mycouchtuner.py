# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 10-11-2018 by JewBMX in Yoda.

import re
import urllib
import urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import proxy


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['mycouchtuner.li','ecouchtuner.eu']
		self.base_link = 'http://mycouchtuner.li'
		self.search_link = '/watch-%s-online/'

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			tvshowtitle = cleantitle.geturl(tvshowtitle)
			url = self.base_link + self.search_link % tvshowtitle
			return url
		except:
			return
 
	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url: return
			r = client.request(url)
			match = re.compile('mycouchtuner\..+?/(.+?)/\' title=\'.+? Season '+season+' Episode '+episode+'\:').findall(r)
			for url in match:
				url = 'http://mycouchtuner.li/%s/' % url
				return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			r = client.request(url)
			match = re.compile('<iframe class=\'lazyload\' data-src=\'//(.+?)/(.+?)\'').findall(r)
			for host,ext in match:
				url = 'https://%s/%s' % (host,ext)
				sources.append({
					'source': host,
					'quality': 'SD',
					'language': 'en',
					'url': url,
					'direct': False,
					'debridonly': False
				}) 
		except Exception:
			return
		return sources

	def resolve(self, url):
		return url