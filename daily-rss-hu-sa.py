#!/usr/bin/python
# -*- coding: iso-8859-2 -*-
# This program generates RSS feeds of the Hungarian Wikipedia's front page anniversaries.

import re, urllib, datetime

from rsslib import WPFeed, CacheItem, date_vars, encode_title

# Settings
settings = {
    'time_range': 7, # purge cache after how many days
    'days_of_week': [1,2,3,4,5,6,7], # Mo: 1, Su: 7
    'output_filename': '/home/t/tgergo/public_html/sa.xml',
    'cache_filename': '/home/t/tgergo/temp/sa_cache.pickle',
    'base_url': 'https://hu.wikipedia.org/',
    'rss_title': u'Wikipédia: Évfordulók',
    'rss_link': 'https://hu.wikipedia.org/wiki/Kezd%C5%91lap',
    'rss_description': u'Aktuális évfordulók a magyar Wikipédia kezdõlapjáról'
}
feed = WPFeed(settings)
template_title = u'Évfordulók/’%(years1)s és ’%(years2)s/%(month)02d-%(day)02d'

def get_content(date):
    title = template_title % date_vars(date)
    url = 'https://hu.wikipedia.org/w/index.php?title=Sablon:%s&action=render' % encode_title(title)
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
            'title'  : u'%(monthname)s %(day)d.: Évfordulók' % date_vars(date),
            'url'    : 'https://hu.wikipedia.org/wiki/Speciális:FeedItem/onthisday/%(years1)d/%(month)d/%(day)d000000/hu' % date_vars(date),
            'content': get_content(date),
        })
    feed.rss(items)
    feed.save()


# Don't run if we're imported
if __name__ == '__main__':
    main()
