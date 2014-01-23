#!/usr/bin/python
# -*- coding: iso-8859-2 -*-

import sys, os
import re, string
import time, datetime, calendar, locale
import urllib
import cPickle
import xml.sax.saxutils

locale.setlocale(locale.LC_TIME, 'en_GB')
currenttimestamp = time.strftime(u'%a, %d %b %Y %H:%M:%S +0000', time.gmtime())
locale.setlocale(locale.LC_TIME, 'hu_HU')

# general settings
settings = {
	'rss_webmaster': u'tgr.huwiki@gmail.com (Tisza Gergő)',
	'program_name': 'WpFeedMaker',
	'program_version': '1.0',
	'program_contact': 'tgr.huwiki@gmail.com',
}

# helpers

def encode_title(s):
	s = s[0:1].upper() + s[1:]
	s = re.sub(' ', '_', s)
	return urllib.quote(s.encode('utf-8'))

def date_vars(date, extend = {}):
	if date.isocalendar()[2] < 4:
		n = 1
	else:
		n = 2
	iso = date.isocalendar()
	dict = {
		'year':      iso[0],
		'years1':    iso[0] % 5,
		'years2':    iso[0] % 5 + 5,
        'month':     date.month,
        'monthname': calendar.month_name[date.month].decode('iso-8859-2'),
        'day' :      date.day,
		'week':      iso[1],
		'dow' :      iso[2],
		'n'   :      n,
	}
	dict.update(extend)
	return dict

# Subclassing of URLopener - sets "User-agent: ", which Wikipedia requires to be set
# to something else than the default "Python-urllib"

class MyURLopener(urllib.URLopener):
	version = settings['program_name'] + "/" + settings['program_version'] + " " + settings['program_contact']

# Caching of HTML from Wikipedia

class CacheItem:
	def __init__(self, html, date, fetchtime):
		self.html = html
		self.date = date
		self.fetchtime = fetchtime

class WPCache:
	def __init__(self, settings):
		self.settings = settings
		self.url_opener = MyURLopener()
		self.filename = self.settings['cache_filename']
		if (os.path.exists(self.filename)):
			file = open(self.filename)
			self.cache = cPickle.load(file)
			file.close()
		else:
			self.cache = {}
	
	def get_html(self, url, date):
		if url in self.cache:
			return self.cache[url].html
		else:
			html = self.url_opener.open(url).read()
			cacheitem = CacheItem(html, date, time.gmtime())
			self.cache[url] = cacheitem
			return html
			
	# Weed out old entries, so cache doesn't get big
	def too_old(self, date):
		return (datetime.date.today() - date).days > self.settings['time_range']
        
	def weed_out_old(self):
		self.cache = dict([x for x in self.cache.items() if not self.too_old(x[1].date)])
 	
	def save(self):
		self.weed_out_old()
		file = open(self.filename, "w")
		p = cPickle.Pickler(file)
		p.dump(self.cache)
		
class WPFeed:
	def __init__(self, settings):
		self.settings = settings
		self.cache = WPCache(self.settings)
    
	def get_html(self, url, date, clean = True):
		html = self.cache.get_html(url, date)
		if clean:
			html = re.sub('\s*<!--[\s\S]*?-->\s*', '', html)
		return html

	def rss_item(self, item):
		return """<item>
<title>%(title)s</title>
<link>%(url)s</link>
<guid isPermaLink="true">%(url)s</guid>
<description>%(escaped_content)s</description>
</item>
""" %   { 
			'title': xml.sax.saxutils.escape(item['title']), 
			'url': item['url'], 
			'escaped_content': xml.sax.saxutils.escape(item['content']),
		}

	def rss(self, items):
		self.xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:blogChannel="http://backend.userland.com/blogChannelModule">

<channel>
<title>%(rss_title)s</title>
<link>%(rss_link)s</link>
<description>%(rss_description)s</description>
<language>hu</language>
<copyright>CC-BY-SA-3.0</copyright>
<lastBuildDate>%(build_date)s</lastBuildDate>
<docs>http://blogs.law.harvard.edu/tech/rss</docs>
<webMaster>%(webmaster)s</webMaster>
<generator>%(generator)s</generator>

%(items)s

</channel>
</rss>
""" %   {
			'rss_title': self.settings['rss_title'], 
			'rss_link': self.settings['rss_link'],
			'rss_description': self.settings['rss_description'],
			'webmaster': settings['rss_webmaster'],
			'build_date': currenttimestamp,
			'items': '\n'.join(map(self.rss_item, items)),
			'generator': settings['program_name'] + ' ' + settings['program_version'],
		}

	def save(self):
		file = open(self.settings['output_filename'], "w")
		file.write(self.xml.encode('utf-8'))
		file.close()
		self.cache.save()
		

def main():
	print "This file cannot be invoked directly" 
	sys.exit(1)	

if __name__ == '__main__':

	main()
