#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Crawles over poznejbrno.cz."""



from HTMLParser import HTMLParseError
from tools import slugify, decode_unicode_entities, log
from tools.database import Database
from tools.downloader import Downloader
from tools.geocoder import Geocoder
from tools.googlemaps import GoogleMaps
import re



def run():
    # connect to db
    db = Database()
    source_id = db.insert_update('sources', {'url': 'http://poznejbrno.cz'})
    
    # fetch all article urls
    url = 'http://poznejbrno.cz/page/%s'
    articles = []
    for i in range(1000):
        log('page', i)
        try:
            links = Downloader(url, i).html().findAll('a', {'rel': 'bookmark'})
            if not links:
                break
            
            for link in links:
                articles.append(link['href'])
                
        except HTMLParseError:
            log('error', 'parsing failure, skipping')
    
    # make it unique
    articles = set(articles)
    
    # process articles
    for url in articles:
        log('article', url)
        try:
            html = Downloader(url).html()
            links = html.findAll(lambda tag: tag.name == 'a' and re.match(r'http://local\.google\.com/maps', tag['href'])) 
            
            # get title & save article
            title = unicode(decode_unicode_entities(html.find('h1', 'entry-title').string))
            article_id = db.insert_update('articles', {'title': title, 'url': url, 'source_id': source_id})
            
            # get & save tags
            tag_ids = []
            for tag in html.find(attrs='post_tags').findAll('a', {'rel': 'tag'}):
                id = db.insert_update('tags', {'name': tag.string, 'slug': slugify(tag.string)})
                tag_ids.append(id)
                
            # get places
            for link in links:
                query = GoogleMaps().parse_link_url(link['href']) # bud 49.234553,16.567812 nebo u'krav\xc3\xad hora'
                log('link', query)
    
                geocoded = Geocoder(query, resolve_coords=False).fetch()
                if geocoded:
                    geocoded['name'] = None
                    place_id = db.insert_update('places', geocoded)
                    
                    # save relations
                    for id in tag_ids:
                        db.insert_update('has_tag', {'place_id': place_id, 'tag_id': id}, last_id=False)
                    db.insert_update('is_about', {'place_id': place_id, 'article_id': article_id}, last_id=False)
            
            db.commit()
                
        except HTMLParseError:
            log('error', 'parsing failure, skipping')
        

        
if __name__ == '__main__':
    run()
    
    
    