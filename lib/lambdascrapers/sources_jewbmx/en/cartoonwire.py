# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 10-10-2018 by JewBMX in Yoda.

import re
import urllib
import urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client

class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['cartoonwire.to']
		self.base_link = 'https://cartoonwire.to'
		self.search_link = '/episode/%s-season-%s-episode-%s/'

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except:
			return
 
	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url: return
			tvshowtitle = url
			url = self.base_link + self.search_link % (tvshowtitle, season, episode)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			r = client.request(url)
			try:
				match = re.compile('var filmId = "(.+?)"').findall(r)
				for film_id in match: 
					
					# VIP
					#server = 'vip'
					#url = 'https://cartoonwire.to/ajax-get-link-stream/?server=' + server + '&filmId=' + film_id
					#r = client.request(url)
					#if r == '':
					#	pass
					#else:
					#	if '2160' in r: quality = '4K'
					#	elif '1080' in r: quality = '1080p'
					#	elif '720' in r: quality = 'HD'
					#	elif '480' in r: quality = 'SD'
					#	else: quality = 'HD'
					#	r = client.request(r)
					#	match = re.compile('<iframe src="(.+?)"').findall(r)
					#	for url in match:
					#		sources.append({
					#			'source': server,
					#			'quality': quality,
					#			'language': 'en',
					#			'url': url,
					#			'direct': False,
					#			'debridonly': False
					#		})
					
					# STREAMANGO
					server = 'streamango'
					url = 'https://cartoonwire.to/ajax-get-link-stream/?server=' + server + '&filmId=' + film_id
					r = client.request(url)
					if r == '':
						pass
					else:
						if '2160' in r: quality = '4K'
						elif '1080' in r: quality = '1080p'
						elif '720' in r: quality = 'HD'
						elif '480' in r: quality = 'SD'
						else: quality = 'HD'
						r = client.request(r)
						match = re.compile('<iframe src="(.+?)"').findall(r)
						for url in match:
							sources.append({
								'source': server,
								'quality': quality,
								'language': 'en',
								'url': url,
								'direct': False,
								'debridonly': False
							})
					
					# OPENLOAD
					server = 'openload'
					url = 'https://cartoonwire.to/ajax-get-link-stream/?server=' + server + '&filmId=' + film_id
					r = client.request(url)
					if r == '':
						pass
					else:
						if '2160' in r: quality = '4K'
						elif '1080' in r: quality = '1080p'
						elif '720' in r: quality = 'HD'
						elif '480' in r: quality = 'SD'
						else: quality = 'HD'
						r = client.request(r)
						match = re.compile('<iframe src="(.+?)"').findall(r)
						for url in match:
							sources.append({
								'source': server,
								'quality': quality,
								'language': 'en',
								'url': url,
								'direct': False,
								'debridonly': False
							})
					
					# RAPIDVIDEO
					server = 'rapidvideo'
					url = 'https://cartoonwire.to/ajax-get-link-stream/?server=' + server + '&filmId=' + film_id
					r = client.request(url)
					if r == '':
						pass
					else:
						if '2160' in r: quality = '4K'
						elif '1080' in r: quality = '1080p'
						elif '720' in r: quality = 'HD'
						elif '480' in r: quality = 'SD'
						else: quality = 'HD'
						r = client.request(r)
						match = re.compile('<iframe src="(.+?)"').findall(r)
						for url in match:
							sources.append({
								'source': server,
								'quality': quality,
								'language': 'en',
								'url': url,
								'direct': False,
								'debridonly': False
							})
					
					# GOOGLE
					server = 'photo'
					url = 'https://cartoonwire.to/ajax-get-link-stream/?server=' + server + '&filmId=' + film_id
					r = client.request(url)
					if r == '':
						pass
					else:
						if '2160' in r: quality = '4K'
						elif '1080' in r: quality = '1080p'
						elif '720' in r: quality = 'HD'
						elif '480' in r: quality = 'SD'
						else: quality = 'HD'
						sources.append({
							'source': 'GDrive',
							'quality': quality,
							'language': 'en',
							'url': r,
							'direct': False,
							'debridonly': False
						})
			except:
				return
		except Exception:
			return
		return sources

	def resolve(self, url):
		return url