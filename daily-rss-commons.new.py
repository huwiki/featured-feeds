#!/usr/bin/python
#
# http://en.wikipedia.org/wiki/User:Skagedal/Fafafa
#
# This program generates RSS feed of Commons' Picture of the Day.

import sys, os, string, datetime, time, urllib, re
import cPickle, xml.sax.saxutils
import types # FIXME see too_old

#
# Settings
#

# ...General
settings = {
	'rss_webmaster': 'tgergo@sch.bme.hu',
	'program_name': 'Fafafa',
	'version': '0.8'
	}

# ...for Picture of the Day
settings_potd = {
	'language': 'hu',
	'entries': 20,
	'output_filename': '/home/t/tgergo/public_html/commons-potd.xml',
	'cache_filename': '/home/t/tgergo/temp/commons-potd_cache.pickle',
	'name_url' : 'http://commons.wikimedia.org/w/index.php?title=Template:Potd/%(year)d-%(month)02d-%(day)02d_(%(lang)s)&action=raw',
	'url': 'http://commons.wikimedia.org/w/index.php?title=Special:ExpandTemplates&input=%(template)s',
	'rss_title_url': 'http://commons.wikimedia.org/wiki/Template:Potd/name/%(lang)s'
	'rss_link': 'http://commons.wikimedia.org/wiki/Commons:Picture_of_the_day',
	'rss_description': 'RSS feed of the Commons Picture of the Day, generated from HTML by ' \
                           '(slightly modified) Fafafa: http://en.wikipedia/wiki/User:Skagedal/Fafafa'
}

# Insert time- and language-related variables into URL

template = """
{| style="width:%(width)dpx; text-align:center;"
|[[Image:{{Potd/%(year)d-%(month)02d-%(day)02d}}|%(width)dpx|]]
|-
| {{lang|%(lang)s|{{ {{#ifexist:Template:Potd/%(year)d-%(month)02d-%(day)02d (%(lang)s)|Potd/%(year)d-%(month)02d-%(day)02d (%(lang)s)|{{#ifexist:Template:Potd/%(year)d-%(month)02d-%(day)02d (%(fallback_lang)s)|Potd/%(year)d-%(month)02d-%(day)02d (%(fallback_lang)s)|empty}}}} }} }}
|}
"""

def calculate_url(url, date, lang=settings['language']):
	return url % { \
                'days_ago': (datetime.date.today() - date).days +1, 'monthname': months[date.month - 1], \
                'day': date.day, 'month': date.month, 'year': date.year, 'lang': lang }

# Subclassing of URLopener - sets "User-agent: ", which Wikipedia requires to be set
# to something else than the default "Python-urllib"

class MyURLopener(urllib.URLopener):
	version = settings['program_name'] + "/" + settings['version']

def too_old(date):
        # FIXME ugly hack to mix dates and date-language tuples in the cache
        if type(date) is types.TupleType:
            date = date[0]
	return (datetime.date.today() - date).days > settings['entries']
	
# Caching of HTML from Wikipedia

class CacheItem:
	def __init__(self, html, fetchtime):
		self.html = html
		self.fetchtime = fetchtime
			
class WPCache:

	def __init__(self, cachefilename):
		self.url_opener = MyURLopener()
		self.filename = cachefilename
		if (os.path.exists(cachefilename)):
			file = open(cachefilename)
			self.cache = cPickle.load(file)
			file.close()
		else:
			self.cache = {}
	
	def get_html(self, date):
		if date in self.cache:
			return self.cache[date].html
		else:
			html = self.url_opener.open(get_content_url(date)).read()
			cacheitem = CacheItem(html, time.gmtime())
			self.cache[date] = cacheitem
			return html
        
        def get_name(self, date, lang):
                if (date, lang) in self.cache:
			return self.cache[(date, lang)].html
                else:
                        html = self.url_opener.open(calculate_url(settings['name_url'], date, lang)).read()
                        cacheitem = CacheItem(html, time.gmtime())
                        self.cache[(date, lang)] = cacheitem
                        return html
                        
	# Weed out old entries, so cache doesn't get big
	def weed_out_old(self):
		self.cache = dict([x for x in self.cache.items() if not too_old(x[0])])
		
	def save(self):
		self.weed_out_old()
		file = open(self.filename, "w")
		p = cPickle.Pickler(file)
		p.dump(self.cache)
		
# Get useful part of the article

def get_section(s, n):
        re_section = re.compile('<h2><span class="mw-headline">%02d</span></h2>(.*?</table>)' % (n), re.DOTALL)
	m = re_section.search(s)
	s = m.group(1)

        return s.strip()

# Get title of article

def get_title(s):
        # get content
        re_content = re.compile('<!--\s*start\s+content\s*-->(.*)<div class="printfooter">', re.DOTALL)
        m = re_content.search(s)
        s = m.group(1)
                
        # strip HTML tags
        re_tag = re.compile('<[^>]*>', re.DOTALL)
        s = re.sub(re_tag, '', s)
        
        # strip superfluous whitespace
        s = re.sub(r'\s+', ' ', s)
        
        return s.strip()

# Create RSS item - expects html filtered by get_content

def rss_item(date, name, content):

	if 'no_title' in settings and settings['no_title']:
		title = "%s %d" % (months[date.month - 1], date.day)
	else:
		title = "%s %d: %s" % (months[date.month - 1], date.day, name)
	return """<item>

<title>%(title)s</title>

<link>%(url)s</link>

<description>%(escaped_content)s</description>

</item>
""" % { 
	'title': title, 
	'url': calculate_url(settings['url'], date), 
	'escaped_content': xml.sax.saxutils.escape(content)}

# Puts the final RSS together

def rss(items):
	return """<?xml version="1.0" encoding="UTF-8"?>

<rss version="2.0" xmlns:blogChannel="http://backend.userland.com/blogChannelModule">

<channel>
<title>%(rss_title)s</title>
<link>%(rss_link)s</link>
<description>%(rss_description)s</description>
<language>en-us</language>
<copyright>Varoius free licenses</copyright>
<lastBuildDate>%(build_date)s</lastBuildDate>
<docs>http://blogs.law.harvard.edu/tech/rss</docs>
<webMaster>%(webmaster)s</webMaster>
<generator>%(generator)s</generator>

%(items)s

</channel>
</rss>
""" % {
	'rss_title': settings['rss_title'], 
	'rss_link': settings['rss_link'],
	'rss_description': settings['rss_description'],
	'webmaster': settings['rss_webmaster'],
	'build_date': time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
	'items': items, 
	'generator': settings['program_name'] + " " + settings['version'] }

# Main

def main():
	settings.update(settings_potd)

	today = datetime.date.today()
	one_day = datetime.timedelta(days = 1)

	cache = WPCache(settings['cache_filename'])
	
	dates = [today - one_day*x for x in range(settings['entries'])]

	def item(date, lang):
                #TODO fall back to english if language not found
                name = get_title(cache.get_name(date, lang))
		content = get_section(cache.get_html(date), date.day)

		return rss_item(date, name, content)

	# Iterate over the items
	items = string.join([item(date, settings['language']) for date in dates], "")
	the_rss = rss(items)

	# Write to file
	file = open(settings['output_filename'], "w")
	file.write(the_rss)
	file.close()
	
	cache.save()

# Don't run if we're imported

if __name__ == '__main__':
	main()
