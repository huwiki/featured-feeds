#!/usr/bin/python
# -*- coding: iso-8859-2 -*-
# This program generates RSS feeds of the Hungarian Wikipedia's front pictures of the day (based on Commons POTD).

import re, urllib, datetime

from rsslib import WPFeed, CacheItem, date_vars, encode_title

# Settings
settings = {
    'time_range': 7, # purge cache after how many days
    'days_of_week': range(1,8), # Mo: 1, Su: 7
    'output_filename': '/home/t/tgergo/public_html/potd.xml',
    'cache_filename': '/home/t/tgergo/temp/potd_cache.pickle',
    'base_url': 'http://hu.wikipedia.org/',
    'rss_title': u'Wikipédia: Kiemelt kép',
    'rss_link': 'http://hu.wikipedia.org/wiki/Kezd%C5%91lap',
    'rss_description': u'Kiemelt képek a magyar Wikipédia kezdőlapjáról'
}
feed = WPFeed(settings)
image_template = u'Napképe/%(year)d-%(month)02d-%(day)02d'
desc_template = u'Napképe/%(year)d-%(month)02d-%(day)02d (hu)'
html_template = """<div style="width: 350px;">
<a href="%(page)s">
<img width="350" src="%(image)s" />
</a>
<br />
<p style="text-align: center;">
%(desc)s
</p>
</div>"""

def get_content_vars(date):
    image_title = image_template % date_vars(date)
    url = 'http://hu.wikipedia.org/w/index.php?title=Sablon:%s&action=raw' % encode_title(image_title)
    content = feed.get_html(url, date).decode('utf-8')
    image = re.sub('<noinclude>.*?</noinclude>', '', content)
    
    image = encode_title(image)
    url = 'http://hu.wikipedia.org/w/api.php?action=query&titles=File:%s&prop=imageinfo&iiurlwidth=350px&iiprop=url&format=xml' % image
    content = feed.get_html(url, date).decode('utf-8')
    try:
        image = re.search('thumburl="(.*?)"', content).group(1)
    except AttributeError:
        image = ''
    try:
        page = re.search('descriptionurl="(.*?)"', content).group(1)
    except AttributeError:
        page = ''
    
    desc_title = desc_template % date_vars(date)
    url = 'http://hu.wikipedia.org/w/index.php?title=Sablon:%s&action=render' % encode_title(desc_title)
    desc = feed.get_html(url, date).decode('utf-8')
    
    return {
        'image': image,
        'page' : page,
        'desc' : desc,
    }

def main():
    today = datetime.date.today()
    one_day = datetime.timedelta(days = 1)
    dates = [today - one_day*x for x in range(settings['time_range'])]
    
    def is_right_day(date):
        return date.isocalendar()[2] in settings['days_of_week']
    dates = filter(is_right_day, dates)    
    
    items = []
    for date in dates:
        content_vars = get_content_vars(date)
        items.append({
            'title'  : u'Nap képe (%(year)d. %(monthname)s %(day)d.)' % date_vars(date),
            'url'    : content_vars['page'],
            'content': html_template % content_vars,
        })
    feed.rss(items)
    feed.save()


# Don't run if we're imported
if __name__ == '__main__':
    main()
