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

import re,urllib,urlparse,json,base64, random

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser
from resources.lib.modules import debrid
from resources.lib.modules import log_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['watchseriesfree.to','seriesfree.to']
		self.base_link = 'https://seriesfree.to/'
		self.search_link = 'https://seriesfree.to/search/%s'
		self.max_conns = 10 
		self.min_srcs = 3

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			query = self.search_link % urllib.quote_plus(cleantitle.query(tvshowtitle))

			
			for i in range(4):
				result = client.request(query, timeout=3)
				if not result == None: break
			

			t = [tvshowtitle] + source_utils.aliases_to_array(aliases)
			t = [cleantitle.get(i) for i in set(t) if i]
			result = re.compile('itemprop="url"\s+href="([^"]+).*?itemprop="name"\s+class="serie-title">([^<]+)', re.DOTALL).findall(result)
			for i in result:
				if cleantitle.get(cleantitle.normalize(i[1])) in t and year in i[1]: url = i[0]

			url = url.encode('utf-8')
			
			
			return url
		except:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url == None: return
			

			url = urlparse.urljoin(self.base_link, url)
			
			for i in range(4):
				result = client.request(url, timeout=3)
				if not result == None: break
			
				

			
			items = dom_parser.parse_dom(result, 'a', attrs={'itemprop':'url'})

			
			
			
			try:	
				
				url = [i.attrs['href'] for i in items if bool(re.compile('"datePublished">%s' % premiered).search(i.content))][0]
			except:
				url = None
				pass  
			
			
			if url == None:
			
				url = [i.attrs['href'] for i in items if bool(re.compile('<span\s*>%s<.*?itemprop="episodeNumber">%s<\/span>' % (season,episode)).search(i.content))][0]
			
			
			url = url.encode('utf-8')
			
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
	
		
	
		try:
			sources = []
			if url == None: return sources

			req = urlparse.urljoin(self.base_link, url)
			
			
			for i in range(4):
				result = client.request(req, timeout=3)
				if not result == None: break
				
				
			
			dom = dom_parser.parse_dom(result, 'div', attrs={'class':'links', 'id': 'noSubs'})
			result = dom[0].content		
			links = re.compile('<i class="fa fa-youtube link-logo"></i>([^<]+).*?href="([^"]+)"\s+class="watch',re.DOTALL).findall(result)
			random.shuffle(links)
			
			
			
			if debrid.status() == True:
				debrid_links = []
				for pair in links:
					for r in debrid.debrid_resolvers:
						if r.valid_url('', pair[0].strip()): debrid_links.append(pair)
				links = debrid_links + links


			
			hostDict = hostDict + hostprDict
			
			conns = 0 
			for pair in links:
			
				
				if conns > self.max_conns and len(sources) > self.min_srcs: break	 

				
				
				host = pair[0].strip()	  
				link = pair[1]
				
				
				
				valid, host = source_utils.is_host_valid(host, hostDict)
				if not valid: continue
				
				
				 
				link = urlparse.urljoin(self.base_link, link)
				for i in range(2):
					result = client.request(link, timeout=3)
					conns += 1
					if not result == None: break	 
				
				
				
				try:
					link = re.compile('href="([^"]+)"\s+class="action-btn').findall(result)[0]
				except: 
					continue
					
					
				
				try:
					u_q, host, direct = source_utils.check_directstreams(link, host)
				except:
					continue
					
				
				link, quality = u_q[0]['url'], u_q[0]['quality']
				

				
				sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': direct, 'debridonly': False})
					
			return sources
		except:
			failure = traceback.format_exc()
			log_utils.log('WATCHSERIES - Exception: \n' + str(failure))
			return sources


	def resolve(self, url):
		return url