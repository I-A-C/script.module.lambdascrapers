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

import re,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

# Working: https://www.best-moviez.ws/deadpool-2-2018-1080p-web-dl-dd5-1-h264-cmrg/
# Working: https://www.best-moviez.ws/deadpool-2-2018
# Working: https://www.best-moviez.ws/deadpool-2
# Working: https://www.best-moviez.ws/deadpool--2--2018
# Failed:  https://www.best-moviez.ws/Deadpool+2+2018

class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['best-moviez.ws']
		self.base_link = 'http://www.best-moviez.ws'
		self.search_link = '/%s'


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

			if debrid.status() == False: raise Exception()

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s s%02de%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
			query = re.sub('[\\\\:;*?"<>|/ \+\']+', '-', query)

			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)
			#log_utils.log('\n\n\n\n\n\nquery, url: %s, %s' % (query,url))
			r = client.request(url)

			
			# grab the (only?) relevant div and cut off the footer
			r = client.parseDOM(r, "div", attrs={'class': 'entry-content'})[0]
			r = re.sub('shareaholic-canvas.+', '', r, flags=re.DOTALL)
		
		
					
			# gather actual <a> links then clear all <a>/<img> to prep for naked-url scan
			# inner text could be useful if url looks like http://somehost.com/ugly_hash_377cbc738eff
			a_txt = ''
			a_url = ''
			a_txt = client.parseDOM(r, "a", attrs={'href': '.+?'})
			a_url = client.parseDOM(r, "a", ret = "href")
			r = re.sub('<a .+?</a>', '', r, flags=re.DOTALL)
			r = re.sub('<img .+?>', '', r, flags=re.DOTALL)	
			
		
			# check pre blocks for size and gather naked-urls
			size = ''			
			pre_txt = []
			pre_url = []
			pres = client.parseDOM(r, "pre", attrs={'style': '.+?'})
			for pre in pres:
				try: size = re.findall('([0-9,\.]+ ?(?:GB|GiB|MB|MiB))', pre)[0]
				except: pass
				
				url0 = re.findall('https?://[^ <"\'\s]+', pre, re.DOTALL) # bad form but works with this site
				txt0 = [size] * len(url0)
				pre_url = pre_url + url0
				pre_txt = pre_txt + txt0 # we're just grabbing raw urls so there's no other info
				
			r = re.sub('<pre .+?</pre>', '', r, flags=re.DOTALL)	

			
			# assume info at page top is true for all movie links, and only movie links
			#  (and that otherwise, only <pre>'s have scrapable sizes)
			size = ''
			if not 'tvshowtitle' in data:
				try: size = " " + re.findall('([0-9,\.]+ ?(?:GB|GiB|MB|MiB))', r)[0]
				except: pass

			
			# get naked urls (after exhausting <a>'s and <pre>'s)
			# note: all examples use full titles in links, so we can be careful
			raw_url = re.findall('https?://[^ <"\'\s]+', r, re.DOTALL) # bad form but works with this site
			raw_txt = [size] * len(raw_url) # we're just grabbing raw urls so there's no other info

			
			# combine the 3 types of scrapes
			pairs = zip(a_url+pre_url+raw_url, a_txt+pre_txt+raw_txt)

			for pair in pairs:
				try:
					url = str(pair[0])
					info = re.sub('<.+?>','',pair[1]) #+ size  # usually (??) no <span> inside
					
					# immediately abandon pairs with undesired traits
					#  (if they stop using urls w/ titles, would need to accomodate here)
					if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
					if not query.lower() in re.sub('[\\\\:;*?"<>|/ \+\'\.]+', '-', url+info).lower(): raise Exception()
					
					
					# establish size0 for this pair: 'size' is pre-loaded for movies only...
					#  ...but prepend 'info' to lead with more-specific sizes (from a <pre>)
					size0 = info + " " + size
					
					
					# grab first reasonable data size from size0 string
					try:
						size0 = re.findall('([0-9,\.]+ ?(?:GB|GiB|MB|MiB))', size0)[0]
						div = 1 if size0.endswith(('GB', 'GiB')) else 1024
						size0 = float(re.sub('[^0-9\.]', '', size0)) / div
						size0 = '%.2f GB' % size0
					except:
						size0 = ''
						pass
					
					
					# process through source_tools and hint with size0 
					quality, info = source_utils.get_release_quality(url,info)
					info.append(size0)
					info = ' | '.join(info)
					#log_utils.log('** pair: [%s / %s] %s' % (quality,info,url))
					
					url = url.encode('utf-8')
					hostDict = hostDict + hostprDict

					valid, host = source_utils.is_host_valid(url, hostDict)
					if not valid: continue
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
									'info': info, 'direct': False, 'debridonly': True})

				except:
					pass

			return sources
		except:
			return sources

	def resolve(self, url):
		return url



'''
EXAMPLE: text urls after "Single Link" (note no "S")
<div class="entry-content">
<div style="text-align:center"><img src="https://i103.fastpic.ru/big/2018/0808/81/371ccc697bd9da5d664322cee07a1581.jpg" /></div>
<div style="text-align:center"><span style="font-weight:bold">Deadpool 2 (2018) 720p BluRay x264 DTS-HDC</span><br />
<span style="font-weight:bold">Language(s)</span>: English<br />
01:59:00 | 1280&#215;536 @ 6200 kb/s | 23.98 fps(r) | DTS, 44100 Hz, 6CH, 1509 kb/s | 6.42 GB<br />
<span style="font-weight:bold">Genre(s)</span>: Action, Adventure, Comedy<br />
<a href="https://www.imdb.com/title/tt5463162/"><span style="font-weight:bold">IMDB</span></a></div>
<p><span id="more-75092"></span></p>
<div style="text-align:center"> Foul-mouthed mutant mercenary Wade Wilson (AKA. Deadpool), brings together a team of fellow mutant rogues to protect a young boy with supernatural abilities from the brutal, time-traveling cyborg, Cable.</p>
...
<span style="font-weight:bold"><span style="color:#FF0000">Download</span></span></p>
<p><span style="font-weight:bold"><span style="color:#00BF00">Single Link</span></span></p>
<p>http://nitroflare.com/view/4424F59C04B5172/Deadpool.2.2018.720p.BluRay.x264.DTS-HDC.mkv</p>
<p><span style="font-weight:bold"><span style="color:#0080FF">NitroFlare</span></span></p>
<p>http://nitroflare.com/view/F8885D081E8036B/Deadpool.2.2018.720p.BluRay.x264.DTS-HDC.part1.rar<br />


EXAMPLE: <a> links after "Single Links" (note now there is an "S")
<div class="entry-content">
...
<p><b><span style="color: #ff0000">DownLoad</b></span></p>
<p><b><span style="color: #ff0000">Single Links</b></span><br />
<a href="https://nitroflare.com/view/B79F3390ED3305B/Avengers.Infinity.War.2018.2160p.UHD.BluRay.x265-SWTYBLZ.mkv">Avengers.Infinity.War.2018.2160p.UHD.BluRay.x265-SWTYBLZ.mkv</a></p>
<p><a href="https://uploadgig.com/file/download/f8e5B103e779F0a4/Avengers.Infinity.War.2018.2160p.UHD.BluRay.x265-SWTYBLZ.mkv">Avengers.Infinity.War.2018.2160p.UHD.BluRay.x265-SWTYBLZ.mkv</a></p>
<p><b><span style="color: #ff0000">NitroFlare</b></span><br />
<a href="https://nitroflare.com/view/9EACE029F149096/Avengers.Infinity.War.2018.2160p.UHD.BluRay.x265-SWTYBLZ.part01.rar">Avengers.Infinity.War.2018.2160p.UHD.BluRay.x265-SWTYBLZ.part01.rar</a><br />
<a href="https://nitroflare.com/view/5F167E50AFBCDD7/Avengers.Infinity.War.2018.2160p.UHD.BluRay.x265-SWTYBLZ.part02.rar">Avengers.Infinity.War.2018.2160p.UHD.BluRay.x265-SWTYBLZ.part02.rar</a><br />


EXAMPLE: <a> link but to a .iso file
<div class="entry-content">
...
<p><b><span style="color: #ff0000">DownLoad</b></span></p>
<p><b><span style="color: #ff0000">Single Link</b></span><br />
<a href="https://nitroflare.com/view/D0ADAE9780B6340/Avengers.Age.Of.Ultron.UHDBD-TERMiNAL.iso">Avengers.Age.Of.Ultron.UHDBD-TERMiNAL.iso</a></p>
<p><a href="https://uploadgig.com/file/download/5c02b57c909968cf/Avengers.Age.Of.Ultron.UHDBD-TERMiNAL.iso">Avengers.Age.Of.Ultron.UHDBD-TERMiNAL.iso</a></p>
<p><b><span style="color: #ff0000">NitroFlare</b></span><br />
<a href="https://nitroflare.com/view/435E34B243AEEC1/Avengers.Age.Of.Ultron.UHDBD-TERMiNAL.part01.rar">Avengers.Age.Of.Ultron.UHDBD-TERMiNAL.part01.rar</a><br />
<a href="https://nitroflare.com/view/D11B2E1CEEB4D00/Avengers.Age.Of.Ultron.UHDBD-TERMiNAL.part02.rar">Avengers.Age.Of.Ultron.UHDBD-TERMiNAL.part02.rar</a><br />


EXAMPLE: Plain text inside sometimes-shared) <p> tags
<div class="entry-content">
...
<span style="font-weight:bold"><span style="color:#FF0000">Download</span></span></p>
<p><span style="font-weight:bold"><span style="color:#00BF00">Single Link</span></span></p>
<p>http://nitroflare.com/view/FBBCB2B4E2FE486/The.Death.of.Superman.2018.1080p.BluRay.DTS.x264-TayTO.mkv</p>
<p>
<span style="font-weight:bold"><span style="color:#0080FF">NitroFlare</span></span></p>
<p>http://nitroflare.com/view/EAF5BF83036A8DE/The.Death.of.Superman.2018.1080p.BluRay.DTS.x264-TayTO.part1.rar<br />
http://nitroflare.com/view/290A3D1480AD822/The.Death.of.Superman.2018.1080p.BluRay.DTS.x264-TayTO.part2.rar<br />



EXAMPLE: tv episode text links in <pre>, by type/quality
<div class="entry-content">
...
<span style="font-weight:bold">[LiNKs]</span></p>
<pre style="background:#BBBBBB"><br />
===================================================<br />
➡ Better.Call.Saul.S04E01.HDTV.x264-SVA<br />
===================================================<br /><br />
http://nitroflare.com/view/8E5BBDBD5378EB2/Better.Call.Saul.S04E01.HDTV.x264-SVA.mkv<br />
https://rapidgator.net/file/b1abba0d3fac85c7b4adecf2b194734d/Better.Call.Saul.S04E01.HDTV.x264-SVA.mkv.html<br />
https://uploadgig.com/file/download/e5c4bf10a454144A/Better.Call.Saul.S04E01.HDTV.x264-SVA.mkv<br />
https://k2s.cc/file/1e8490e210630/Better.Call.Saul.S04E01.HDTV.x264-SVA.mkv<br /><br />
===================================================<br />
➡ Better.Call.Saul.S04E01.720p.HDTV.x264-AVS<br />
===================================================<br /><br />
http://nitroflare.com/view/338D7D912CF954E/Better.Call.Saul.S04E01.720p.HDTV.x264-AVS.mkv<br />
https://rapidgator.net/file/f016b7ef0aed23a7eda75b459567a46a/Better.Call.Saul.S04E01.720p.HDTV.x264-AVS.mkv.html<br />
https://uploadgig.com/file/download/d671D3e4dD7e9385/Better.Call.Saul.S04E01.720p.HDTV.x264-AVS.mkv<br />
https://k2s.cc/file/9622e3c5abda5/Better.Call.Saul.S04E01.720p.HDTV.x264-AVS.mp4<br /><br />
===================================================<br />
➡ Better.Call.Saul.S04E01.HDTV.XviD-AFG [P2P]<br />
===================================================<br /><br />
http://nitroflare.com/view/DC7D1E0637F69DE/Better.Call.Saul.S04E01.XviD-AFG.avi<br />
https://rapidgator.net/file/e07a34e09bf8fa8490096a556106c7a3/Better.Call.Saul.S04E01.XviD-AFG.avi.html<br />
https://uploadgig.com/file/download/939Ddb7e78ba3994/Better.Call.Saul.S04E01.XviD-AFG.avi<br />
https://k2s.cc/file/7511e23d723cc/Better.Call.Saul.S04E01.XviD-AFG.mp4<br />
</pre>
'''
