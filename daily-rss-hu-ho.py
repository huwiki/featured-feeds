#!/usr/bin/python
# -*- coding: iso-8859-2 -*-
# This program generates RSS feeds of the Hungarian Wikipedia's front page holidays.

import re, urllib, datetime

from rsslib import WPFeed, CacheItem, date_vars, encode_title

# Settings
settings = {
    'time_range': 7, # purge cache after how many days
    'days_of_week': [1,2,3,4,5,6,7], # Mo: 1, Su: 7
    'output_filename': '/home/t/tgergo/public_html/ho.xml',
    'cache_filename': '/home/t/tgergo/temp/ho_cache.pickle',
    'base_url': 'http://hu.wikipedia.org/',
    'rss_title': u'Wikipédia: Ünnepek',
    'rss_link': 'http://hu.wikipedia.org/wiki/Kezd%C5%91lap',
    'rss_description': u'Aktuális ünnepek a magyar Wikipédia kezdőlapjáról'
}
feed = WPFeed(settings)
template_title = u'Ünnepek/%(month)02d-%(day)02d'

def get_content(date):
    title = template_title % date_vars(date)
    url = 'http://hu.wikipedia.org/w/index.php?title=Sablon:%s&action=render' % encode_title(title)
    content = feed.get_html(url, date).decode('utf-8')
    return content

def main():
    today = datetime.date.today()
    one_day = datetime.timedelta(days = 1)
    dates = [today - one_day*x for x in range(settings['time_range'])]
    
    def is_right_day(date):
        return date.isocalendar()[2] in settings['days_of_week']
    dates = filter(is_right_day, dates)    
    
    items = []
    for date in dates:
        items.append({
            'title'  : u'%(monthname)s %(day)d: Ünnepek' % date_vars(date),
            'url'    : 'http://hu.wikipedia.org/wiki/#%(month)d/%(day)d' % date_vars(date),
            'content': get_content(date),
        })
    feed.rss(items)
    feed.save()


# Don't run if we're imported
if __name__ == '__main__':
    main()
