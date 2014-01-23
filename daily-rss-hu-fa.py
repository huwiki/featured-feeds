#!/usr/bin/python
# -*- coding: iso-8859-2 -*-
# This program generates RSS feeds of the Hungarian Wikipedia's front page articles.

import re, urllib, datetime

from rsslib import WPFeed, CacheItem, date_vars, encode_title

# Settings
settings = {
    'time_range': 14, # purge cache after how many days
    'days_of_week': [1, 4], # Mo: 1, Su: 7
    'output_filename': '/home/t/tgergo/public_html/fa.xml',
    'cache_filename': '/home/t/tgergo/temp/fa_cache.pickle',
    'base_url': 'http://hu.wikipedia.org/',
    'rss_title': u'Wikipédia: Kiemelt szócikk',
    'rss_link': 'http://hu.wikipedia.org/wiki/Kezd%C5%91lap',
    'rss_description': u'Kiemelt szócikkek a magyar Wikipédia kezdőlapjáról'
}
feed = WPFeed(settings)
template_title = u'Kezdőlap kiemelt cikkei/%(year)d-%(week)d-%(n)d'

def get_content(date):
    title = template_title % date_vars(date)
    url = 'http://hu.wikipedia.org/w/index.php?title=Sablon:%s&action=render' % encode_title(title)
    content = feed.get_html(url, date).decode('utf-8')
    return content

def unicode_decode(match):
    codepoint = match.group(1)
    return unichr(int(codepoint, 16))

def get_title(date):
    api_call = 'http://hu.wikipedia.org/w/api.php?action=expandtemplates&text={{Sablon:%(page)s|%(year)s|%(week)s|%(n)s}}&format=yaml'
    url = api_call % date_vars(date, {
        'page': encode_title(u'Kezdőlapra került szócikkek listája'),
    })
    yaml = feed.get_html(url, date).decode('utf-8')
    m = re.search(r'"\*":"(.+?)"', yaml, re.MULTILINE)
    title_json = m.group(1)
    title = re.sub(r'\\u([\da-f]{4})', unicode_decode, title_json)
    return title

def main():
    today = datetime.date.today()
    one_day = datetime.timedelta(days = 1)
    dates = [today - one_day*x for x in range(settings['time_range'])]
    
    def is_right_day(date):
        return date.isocalendar()[2] in settings['days_of_week']
    dates = filter(is_right_day, dates)
    
    items = []
    for date in dates:
        title = get_title(date)
        items.append({
            'title'  : u'%(week)d. hét / %(n)d.: %(title)s' % date_vars(date, {'title': title}),
            'url'    : 'http://hu.wikipedia.org/wiki/%s' % encode_title(title),
            'content': get_content(date),
        })
    feed.rss(items)
    feed.save()


# Don't run if we're imported
if __name__ == '__main__':
    main()
