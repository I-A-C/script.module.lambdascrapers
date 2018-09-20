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
import abc
import urllib2
import urllib
import urlparse
import cookielib
import xbmc
import xbmcaddon
import xbmcgui
import os
import re
import time
import base64
from StringIO import StringIO
import gzip
import datetime
import json
import sys
from salts_lib import log_utils
from salts_lib.trans_utils import i18n
from salts_lib import cloudflare
from salts_lib import pyaes
from salts_lib.db_utils import DB_Connection
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import USER_AGENT
from salts_lib.constants import QUALITIES
from salts_lib.constants import HOST_Q
from salts_lib.constants import Q_ORDER
from salts_lib.constants import BLOG_Q_MAP
import threading

BASE_URL = ''
CAPTCHA_BASE_URL = 'http://www.google.com/recaptcha/api'
COOKIEPATH = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
SHORT_MONS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
Q_LIST = [item[0] for item in sorted(Q_ORDER.items(), key=lambda x:x[1])]

class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        log_utils.log('Stopping Redirect', xbmc.LOGDEBUG)
        return response

    https_response = http_response

abstractstaticmethod = abc.abstractmethod
class abstractclassmethod(classmethod):

    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)

DEFAULT_TIMEOUT = 30

class Scraper(object):
    __metaclass__ = abc.ABCMeta
    base_url = BASE_URL
    db_connection = None
    worker_id = None

    def __init__(self, timeout=DEFAULT_TIMEOUT):
        pass

    @abstractclassmethod
    def provides(cls):
        """
        Must return a list/set/frozenset of VIDEO_TYPES that are supported by this scraper. Is a class method so that instances of the class
        don't have to be instantiated to determine they are not useful

        * Datatypes set or frozenset are preferred as existence checking is faster with sets
        """
        raise NotImplementedError

    @abstractclassmethod
    def get_name(cls):
        """
        Must return a string that is a name that will be used through out the UI and DB to refer to urls from this source
        Should be descriptive enough to be recognized but short enough to be presented in the UI
        """
        raise NotImplementedError

    @abc.abstractmethod
    def resolve_link(self, link):
        """
        Must return a string that is a urlresolver resolvable link given a link that this scraper supports

        link: a url fragment associated with this site that can be resolved to a hoster link

        * The purpose is many streaming sites provide the actual hoster link in a separate page from link
        on the video page.
        * This method is called for the user selected source before calling urlresolver on it.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def format_source_label(self, item):
        """
        Must return a string that is to be the label to be used for this source in the "Choose Source" dialog

        item: one element of the list that is returned from get_sources for this scraper
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_sources(self, video):
        """
        Must return a list of dictionaries that are potential link to hoster sites (or links to links to hoster sites)
        Each dictionary must contain elements of at least:
            * multi-part: True if this source is one part of a whole
            * class: a reference to an instance of the scraper itself
            * host: the hostname of the hoster
            * url: the url that is a link to a hoster, or a link to a page that this scraper can resolve to a link to a hoster
            * quality: one of the QUALITIES values, or None if unknown; users can sort sources by quality
            * views: count of the views from the site for this source or None is unknown; Users can sort sources by views
            * rating: a value between 0 and 100; 0 being worst, 100 the best, or None if unknown. Users can sort sources by rating.
            * direct: True if url is a direct link to a media file; False if not. If not present; assumption is direct
            * other keys are allowed as needed if they would be useful (e.g. for format_source_label)

        video is an object of type ScraperVideo:
            video_type: one of VIDEO_TYPES for whatever the sources should be for
            title: the title of the tv show or movie
            year: the year of the tv show or movie
            season: only present for tv shows; the season number of the video for which sources are requested
            episode: only present for tv shows; the episode number of the video for which sources are requested
            ep_title: only present for tv shows; the episode title if available
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_url(self, video):
        """
        Must return a url for the site this scraper is associated with that is related to this video.

        video is an object of type ScraperVideo:
            video_type: one of VIDEO_TYPES this url is for (e.g. EPISODE urls might be different than TVSHOW urls)
            title: the title of the tv show or movie
            year: the year of the tv show or movie
            season: only present for season or episode VIDEO_TYPES; the season number for the url being requested
            episode: only present for season or episode VIDEO_TYPES; the episode number for the url being requested
            ep_title: only present for tv shows; the episode title if available

        * Generally speaking, domain should not be included
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, video_type, title, year):
        """
        Must return a list of results returned from the site associated with this scraper when doing a search using the input parameters

        If it does return results, it must be a list of dictionaries. Each dictionary must contain at least the following:
            * title: title of the result
            * year: year of the result
            * url: a url fragment that is the url on the site associated with this scraper for this season result item

        video_type: one of the VIDEO_TYPES being searched for. Only tvshows and movies are expected generally
        title: the title being search for
        year: the year being search for

        * Method must be provided, but can raise NotImplementedError if search not available on the site
        """
        raise NotImplementedError

    @classmethod
    def get_settings(cls):
        """
        Returns a list of settings to be used for this scraper. Settings are automatically checked for updates every time scrapers are imported
        The list returned by each scraper is aggregated into a big settings.xml string, and then if it differs from the current settings xml in the Scrapers category
        the existing settings.xml fragment is removed and replaced by the new string
        """
        name = cls.get_name()
        return ['         <setting id="%s-enable" type="bool" label="%s %s" default="true" visible="true"/>' % (name, name, i18n('enabled')),
                    '         <setting id="%s-base_url" type="text" label="    %s" default="%s" visible="eq(-1,true)"/>' % (name, i18n('base_url'), cls.base_url),
                    '         <setting id="%s-sub_check" type="bool" label="    %s" default="true" visible="eq(-2,true)"/>' % (name, i18n('page_existence')),
                    '         <setting id="%s_try" type="number" default="0" visible="false"/>' % (name),
                    '         <setting id="%s_fail" type="number" default="0" visible="false"/>' % (name),
                    '         <setting id="%s_check" type="number" default="0" visible="false"/>' % (name), ]

    @classmethod
    def _disable_sub_check(cls, settings):
        for i in reversed(xrange(len(settings))):
            if 'sub_check' in settings[i]:
                settings[i] = settings[i].replace('default="true"', 'default="false"')
        return settings

    def _default_get_url(self, video):
        temp_video_type = video.video_type
        if video.video_type == VIDEO_TYPES.EPISODE: temp_video_type = VIDEO_TYPES.TVSHOW
        url = None
        self.create_db_connection()

        result = self.db_connection.get_related_url(temp_video_type, video.title, video.year, self.get_name())
        if result:
            url = result[0][0]
            log_utils.log('Got local related url: |%s|%s|%s|%s|%s|' % (temp_video_type, video.title, video.year, self.get_name(), url))
        else:
            results = self.search(temp_video_type, video.title, video.year)
            if results:
                url = results[0]['url']
                self.db_connection.set_related_url(temp_video_type, video.title, video.year, self.get_name(), url)

        if url and video.video_type == VIDEO_TYPES.EPISODE:
            result = self.db_connection.get_related_url(VIDEO_TYPES.EPISODE, video.title, video.year, self.get_name(), video.season, video.episode)
            if result:
                url = result[0][0]
                log_utils.log('Got local related url: |%s|%s|%s|' % (video, self.get_name(), url))
            else:
                show_url = url
                url = self._get_episode_url(show_url, video)
                if url:
                    self.db_connection.set_related_url(VIDEO_TYPES.EPISODE, video.title, video.year, self.get_name(), url, video.season, video.episode)

        return url

    def _cached_http_get(self, url, base_url, timeout, cookies=None, data=None, multipart_data=None, headers=None, allow_redirect=True, cache_limit=8):
        if cookies is None: cookies = {}
        if timeout == 0: timeout = None
        if headers is None: headers = {}
        referer = headers['Referer'] if 'Referer' in headers else url
        log_utils.log('Getting Url: %s cookie=|%s| data=|%s| extra headers=|%s|' % (url, cookies, data, headers))
        self.create_db_connection()
        _, html = self.db_connection.get_cached_url(url, cache_limit)
        if html:
            log_utils.log('Returning cached result for: %s' % (url), xbmc.LOGDEBUG)
            return html

        try:
            self.cj = self._set_cookies(base_url, cookies)
            if data is not None: data = urllib.urlencode(data, True)
            if multipart_data is not None:
                headers['Content-Type'] = 'multipart/form-data; boundary=X-X-X'
                data = multipart_data

            request = urllib2.Request(url, data=data)
            request.add_header('User-Agent', USER_AGENT)
            request.add_unredirected_header('Host', request.get_host())
            request.add_unredirected_header('Referer', referer)
            for key in headers: request.add_header(key, headers[key])
            self.cj.add_cookie_header(request)
            if not allow_redirect:
                opener = urllib2.build_opener(NoRedirection)
                urllib2.install_opener(opener)
            else:
                opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
                urllib2.install_opener(opener)

            response = urllib2.urlopen(request, timeout=timeout)
            self.cj.extract_cookies(response, request)
            if xbmcaddon.Addon().getSetting('cookie_debug') == 'true':
                log_utils.log('Response Cookies: %s - %s' % (url, self.cookies_as_str(self.cj)), xbmc.LOGDEBUG)
            self.__fix_bad_cookies()
            self.cj.save(ignore_discard=True)
            if not allow_redirect and response.getcode() in [301, 302, 303, 307]:
                return response.info().getheader('Location')
            
            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                html = f.read()
            else:
                html = response.read()
        except urllib2.HTTPError as e:
            if e.code == 503 and 'cf-browser-verification' in e.read():
                html = cloudflare.solve(url, self.cj)
                if not html:
                    return ''
            else:
                log_utils.log('Error (%s) during scraper http get: %s' % (str(e), url), xbmc.LOGWARNING)
                return ''
        except Exception as e:
            log_utils.log('Error (%s) during scraper http get: %s' % (str(e), url), xbmc.LOGWARNING)
            return ''

        self.db_connection.cache_url(url, html)
        return html

    def _set_cookies(self, base_url, cookies):
        cookie_file = os.path.join(COOKIEPATH, '%s_cookies.lwp' % (self.get_name()))
        cj = cookielib.LWPCookieJar(cookie_file)
        try: cj.load(ignore_discard=True)
        except: pass
        if xbmcaddon.Addon().getSetting('cookie_debug') == 'true':
            log_utils.log('Before Cookies: %s - %s' % (self, self.cookies_as_str(cj)), xbmc.LOGDEBUG)
        domain = urlparse.urlsplit(base_url).hostname
        for key in cookies:
            c = cookielib.Cookie(0, key, str(cookies[key]), port=None, port_specified=False, domain=domain, domain_specified=True,
                                domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=False, comment=None,
                                comment_url=None, rest={})
            cj.set_cookie(c)
        cj.save(ignore_discard=True)
        if xbmcaddon.Addon().getSetting('cookie_debug') == 'true':
            log_utils.log('After Cookies: %s - %s' % (self, self.cookies_as_str(cj)), xbmc.LOGDEBUG)
        return cj

    def cookies_as_str(self, cj):
        s = ''
        c = cj._cookies
        for domain in c:
            s += '{%s: ' % (domain)
            for path in c[domain]:
                s += '{%s: ' % (path)
                for cookie in c[domain][path]:
                    s += '{%s=%s}' % (cookie, c[domain][path][cookie].value)
                s += '}'
            s += '} '
        return s
                    
    def __fix_bad_cookies(self):
        c = self.cj._cookies
        for domain in c:
            for path in c[domain]:
                for key in c[domain][path]:
                    cookie = c[domain][path][key]
                    if cookie.expires > sys.maxint:
                        log_utils.log('Fixing cookie expiration for %s: was: %s now: %s' % (key, cookie.expires, sys.maxint))
                        cookie.expires = sys.maxint
        
    def _do_recaptcha(self, key, tries=None, max_tries=None):
        challenge_url = CAPTCHA_BASE_URL + '/challenge?k=%s' % (key)
        html = self._cached_http_get(challenge_url, CAPTCHA_BASE_URL, timeout=DEFAULT_TIMEOUT, cache_limit=0)
        match = re.search("challenge\s+\:\s+'([^']+)", html)
        captchaimg = 'http://www.google.com/recaptcha/api/image?c=%s' % (match.group(1))
        img = xbmcgui.ControlImage(450, 0, 400, 130, captchaimg)
        wdlg = xbmcgui.WindowDialog()
        wdlg.addControl(img)
        wdlg.show()
        header = 'Type the words in the image'
        if tries and max_tries:
            header += ' (Try: %s/%s)' % (tries, max_tries)
        kb = xbmc.Keyboard('', header, False)
        kb.doModal()
        solution = ''
        if kb.isConfirmed():
            solution = kb.getText()
            if not solution:
                raise Exception('You must enter text in the image to access video')
        wdlg.close()
        return {'recaptcha_challenge_field': match.group(1), 'recaptcha_response_field': solution}

    def _default_get_episode_url(self, show_url, video, episode_pattern, title_pattern='', airdate_pattern=''):
        log_utils.log('Default Episode Url: |%s|%s|%s|' % (self.base_url, show_url, str(video).decode('utf-8', 'replace')), xbmc.LOGDEBUG)
        url = urlparse.urljoin(self.base_url, show_url)
        html = self._http_get(url, cache_limit=2)
        if html:
            force_title = self._force_title(video)

            if not force_title:
                match = re.search(episode_pattern, html, re.DOTALL)
                if match:
                    url = match.group(1)
                    return url.replace(self.base_url, '')

                if xbmcaddon.Addon().getSetting('airdate-fallback') == 'true' and airdate_pattern and video.ep_airdate:
                    airdate_pattern = airdate_pattern.replace('{year}', str(video.ep_airdate.year))
                    airdate_pattern = airdate_pattern.replace('{month}', str(video.ep_airdate.month))
                    airdate_pattern = airdate_pattern.replace('{p_month}', '%02d' % (video.ep_airdate.month))
                    airdate_pattern = airdate_pattern.replace('{month_name}', MONTHS[video.ep_airdate.month - 1])
                    airdate_pattern = airdate_pattern.replace('{short_month}', SHORT_MONS[video.ep_airdate.month - 1])
                    airdate_pattern = airdate_pattern.replace('{day}', str(video.ep_airdate.day))
                    airdate_pattern = airdate_pattern.replace('{p_day}', '%02d' % (video.ep_airdate.day))
                    log_utils.log('Air Date Pattern: %s' % (airdate_pattern), xbmc.LOGDEBUG)

                    match = re.search(airdate_pattern, html, re.DOTALL | re.I)
                    if match:
                        url = match.group(1)
                        return url.replace(self.base_url, '')
            else:
                log_utils.log('Skipping S&E matching as title search is forced on: %s' % (video.trakt_id), xbmc.LOGDEBUG)

            if (force_title or xbmcaddon.Addon().getSetting('title-fallback') == 'true') and video.ep_title and title_pattern:
                norm_title = self._normalize_title(video.ep_title)
                for match in re.finditer(title_pattern, html, re.DOTALL | re.I):
                    url, title = match.groups()
                    if norm_title == self._normalize_title(title):
                        return url.replace(self.base_url, '')

    def _force_title(self, video):
            trakt_str = xbmcaddon.Addon().getSetting('force_title_match')
            trakt_list = trakt_str.split('|') if trakt_str else []
            return str(video.trakt_id) in trakt_list

    def _normalize_title(self, title):
        new_title = title.upper()
        new_title = re.sub('[^A-Za-z0-9]', '', new_title)
        # log_utils.log('In title: |%s| Out title: |%s|' % (title,new_title), xbmc.LOGDEBUG)
        return new_title

    def _blog_proc_results(self, html, post_pattern, date_format, video_type, title, year):
        results = []
        match = re.search('(.*?)\s*S\d+E\d+\s*', title)
        if match:
            show_title = match.group(1)
        else:
            match = re.search('(.*?)\s*\d{4}\.\d{2}\.\d{2}\s*', title)
            if match:
                show_title = match.group(1)
            else:
                show_title = title
        norm_title = self._normalize_title(show_title)

        filter_days = datetime.timedelta(days=int(xbmcaddon.Addon().getSetting('%s-filter' % (self.get_name()))))
        today = datetime.date.today()
        for match in re.finditer(post_pattern, html, re.DOTALL):
            post_data = match.groupdict()
            post_title = post_data['post_title']
            if 'quality' in post_data:
                post_title += '- [%s]' % (post_data['quality'])

            if filter_days:
                try: post_date = datetime.datetime.strptime(post_data['date'], date_format).date()
                except TypeError: post_date = datetime.datetime(*(time.strptime(post_data['date'], date_format)[0:6])).date()
                if today - post_date > filter_days:
                    continue

            match_year = ''
            match_title = ''
            post_title = post_title.replace('&#8211;', '-')
            post_title = post_title.replace('&#8217;', "'")
            full_title = post_title
            if video_type == VIDEO_TYPES.MOVIE:
                match = re.search('(.*?)\s*[\[(]?(\d{4})[)\]]?\s*(.*)', post_title)
                if match:
                    match_title, match_year, extra_title = match.groups()
                    full_title = '%s [%s]' % (match_title, extra_title)
            else:
                match = re.search('(.*?)\s*S\d+E\d+\s*(.*)', post_title)
                if match:
                    match_title, extra_title = match.groups()
                    full_title = '%s [%s]' % (match_title, extra_title)
                else:
                    match = re.search('(.*?)\s*\d{4}[ .]?\d{2}[ .]?\d{2}\s*(.*)', post_title)
                    if match:
                        match_title, extra_title = match.groups()
                        full_title = '%s [%s]' % (match_title, extra_title)

            match_norm_title = self._normalize_title(match_title)
            if (match_norm_title in norm_title or norm_title in match_norm_title) and (not year or not match_year or year == match_year):
                result = {'url': post_data['url'].replace(self.base_url, ''), 'title': full_title, 'year': match_year}
                results.append(result)
        return results
    
    def _blog_get_url(self, video, delim='.'):
        url = None
        self.create_db_connection()
        result = self.db_connection.get_related_url(video.video_type, video.title, video.year, self.get_name(), video.season, video.episode)
        if result:
            url = result[0][0]
            log_utils.log('Got local related url: |%s|%s|%s|%s|%s|' % (video.video_type, video.title, video.year, self.get_name(), url))
        else:
            select = int(xbmcaddon.Addon().getSetting('%s-select' % (self.get_name())))
            if video.video_type == VIDEO_TYPES.EPISODE:
                temp_title = re.sub('[^A-Za-z0-9 ]', '', video.title)
                if not self._force_title(video):
                    search_title = '%s S%02dE%02d' % (temp_title, int(video.season), int(video.episode))
                    fallback_search = '%s %s' % (temp_title, video.ep_airdate.strftime('%Y{0}%m{0}%d'.format(delim)))
                else:
                    if not video.ep_title: return None
                    search_title = '%s %s' % (temp_title, video.ep_title)
                    fallback_search = ''
            else:
                search_title = '%s %s' % (video.title, video.year)
                fallback_search = ''

            results = self.search(video.video_type, search_title, video.year)
            if not results and fallback_search:
                results = self.search(video.video_type, fallback_search, video.year)
            if results:
                # TODO: First result isn't always the most recent...
                best_result = results[0]
                if select != 0:
                    best_qorder = 0
                    for result in results:
                        match = re.search('\[(.*)\]$', result['title'])
                        if match:
                            q_str = match.group(1)
                            quality = self._blog_get_quality(video, q_str, '')
                            # print 'result: |%s|%s|%s|%s|' % (result, q_str, quality, Q_ORDER[quality])
                            if Q_ORDER[quality] > best_qorder:
                                # print 'Setting best as: |%s|%s|%s|%s|' % (result, q_str, quality, Q_ORDER[quality])
                                best_result = result
                                best_qorder = Q_ORDER[quality]

                url = best_result['url']
                self.db_connection.set_related_url(video.video_type, video.title, video.year, self.get_name(), url)
        return url

    def _blog_get_quality(self, video, q_str, host):
        """
        Use the q_str to determine the post quality; then use the host to determine host quality
        allow the host to drop the quality but not increase it
        """
        q_str.replace(video.title, '')
        q_str.replace(str(video.year), '')
        q_str = q_str.upper()

        post_quality = None
        for key in Q_LIST:
            if any(q in q_str for q in BLOG_Q_MAP[key]):
                post_quality = key

        return self._get_quality(video, host, post_quality)

    def _get_quality(self, video, host, base_quality=None):
        # Assume movies are low quality, tv shows are high quality
        if base_quality is None:
            if video.video_type == VIDEO_TYPES.MOVIE:
                quality = QUALITIES.LOW
            else:
                quality = QUALITIES.HIGH
        else:
            quality = base_quality

        host_quality = None
        if host:
            hl = host.lower()
            for key in HOST_Q:
                if any(hostname in hl for hostname in HOST_Q[key]):
                    host_quality = key
                    break

        # log_utils.log('q_str: %s, host: %s, post q: %s, host q: %s' % (q_str, host, post_quality, host_quality), xbmc.LOGDEBUG)
        if host_quality is not None and Q_ORDER[host_quality] < Q_ORDER[quality]:
            quality = host_quality

        return quality

    def _width_get_quality(self, width):
        width = int(width)
        if width > 1280:
            quality = QUALITIES.HD1080
        elif width > 800:
            quality = QUALITIES.HD720
        elif width > 640:
            quality = QUALITIES.HIGH
        elif width > 320:
            quality = QUALITIES.MEDIUM
        else:
            quality = QUALITIES.LOW
        return quality

    def _height_get_quality(self, height):
        height = int(height)
        if height > 800:
            quality = QUALITIES.HD1080
        elif height > 480:
            quality = QUALITIES.HD720
        elif height >= 400:
            quality = QUALITIES.HIGH
        elif height > 200:
            quality = QUALITIES.MEDIUM
        else:
            quality = QUALITIES.LOW
        return quality

    def _gv_get_quality(self, stream_url):
        if 'itag=18' in stream_url or '=m18' in stream_url:
            return QUALITIES.MEDIUM
        elif 'itag=22' in stream_url or '=m22' in stream_url:
            return QUALITIES.HD720
        elif 'itag=34' in stream_url or '=m34' in stream_url:
            return QUALITIES.HIGH
        elif 'itag=35' in stream_url or '=m35' in stream_url:
            return QUALITIES.HIGH
        elif 'itag=37' in stream_url or '=m37' in stream_url:
            return QUALITIES.HD1080
        else:
            return QUALITIES.HIGH
    
    def _get_sucuri_cookie(self, html):
        if 'sucuri_cloudproxy_js' in html:
            match = re.search("S\s*=\s*'([^']+)", html)
            if match:
                s = base64.b64decode(match.group(1))
                s = s.replace(' ', '')
                s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
                s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
                s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
                s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
                s = re.sub(';location.reload\(\);', '', s)
                s = re.sub(r'\n', '', s)
                s = re.sub(r'document\.cookie', 'cookie', s)
                try:
                    cookie = ''
                    exec(s)
                    match = re.match('([^=]+)=(.*)', cookie)
                    if match:
                        return {match.group(1): match.group(2)}
                except Exception as e:
                    log_utils.log('Exception during sucuri js: %s' % (e), xbmc.LOGWARNING)
        
        return {}
        
    def _get_direct_hostname(self, link):
        host = urlparse.urlparse(link).hostname
        if host and any([h for h in ['google', 'picasa'] if h in host]):
            return 'gvideo'
        else:
            return self.get_name()
    
    def _parse_google(self, link):
        sources = []
        i = link.rfind('#')
        if i > -1:
            link_id = link[i + 1:]
            html = self._http_get(link, cache_limit=.5)
            match = re.search('feedPreload:\s*(.*}]}})},', html, re.DOTALL)
            if match:
                try:
                    js = json.loads(match.group(1))
                except ValueError:
                    log_utils.log('Invalid JSON returned for: %s' % (link), xbmc.LOGWARNING)
                else:
                    for item in js['feed']['entry']:
                        if item['gphoto$id'] == link_id:
                            for media in item['media']['content']:
                                if media['type'].startswith('video'):
                                    sources.append(media['url'].replace('%3D', '='))

        return sources

    def _gk_decrypt(self, key, cipher_link):
        try:
            key += (24 - len(key)) * '\0'
            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationECB(key))
            plain_text = decrypter.feed(cipher_link.decode('hex'))
            plain_text += decrypter.feed()
            plain_text = plain_text.split('\0', 1)[0]
        except Exception as e:
            log_utils.log('Exception (%s) during %s gk decrypt: cipher_link: %s' % (e, self.get_name(), cipher_link), xbmc.LOGWARNING)
            plain_text = ''

        return plain_text
    
    def create_db_connection(self):
        worker_id = threading.current_thread().ident
        # create a connection if we don't have one or it was created in a different worker
        if self.db_connection is None or self.worker_id != worker_id:
            self.db_connection = DB_Connection()
            self.worker_id = worker_id
