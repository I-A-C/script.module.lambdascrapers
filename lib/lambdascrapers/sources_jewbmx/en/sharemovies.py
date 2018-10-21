# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 10-11-2018 by JewBMX in Yoda.

import base64
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
		self.domains = ['sharemovies.net']
		self.base_link = 'http://sharemovies.net'
		self.search_link = '/search-movies/%s.html'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			q = cleantitle.geturl(title)
			q2 = q.replace('-','+')
			url = self.base_link + self.search_link % q2
			r = client.request(url)
			match = re.compile('<div class="title"><a href="(.+?)">'+title+'</a></div>').findall(r)
			for url in match:
				return url
		except:
			return
			
	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except:
			return
 
	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url: return
			
			q = url + '-season-' + season
			q2 = url.replace('-','+')
			url = self.base_link + self.search_link % q2
			r = client.request(url)
			match = re.compile('<div class="title"><a href="(.+?)-'+q+'\.html"').findall(r)
			for url in match:
				url = '%s-%s.html' % (url,q)
				r = client.request(url)
				match = re.compile('<a class="episode episode_series_link" href="(.+?)">' + episode + '</a>').findall(r)
				for url in match:
					return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			r = client.request(url)
			try:
				match = re.compile('themes/movies/img/icon/server/(.+?)\.png" width="16" height="16" /> <a href="(.+?)">Version ').findall(r)
				for host, url in match:
					if host == 'internet':
						pass
					else:
						sources.append({
							'source': host,
							'quality': 'SD',
							'language': 'en',
							'url': url,
							'direct': False,
							'debridonly': False
						})
			except:
				return
		except Exception:
			return
		return sources

	def resolve(self, url):
		r = client.request(url)
		match = re.compile('Base64\.decode\("(.+?)"').findall(r)
		for iframe in match:
			iframe = base64.b64decode(iframe)
			match = re.compile('src="(.+?)"').findall(iframe)
			for url in match:
				return url