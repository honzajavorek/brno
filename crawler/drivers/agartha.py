#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Crawles over agartha.cz."""



from tools import log
from tools.database import Database
from tools.downloader import Downloader
from tools.geocoder import Geocoder
import re



def run():
    # connect to db
    db = Database()
    source_id = db.insert_update('sources', {'url': 'http://www.agartha.cz'})
    
    # prepare
    tag_id = db.insert_update('tags', {'name': u'podzemí', 'slug': 'podzemi'})
    
    BIAS = {u'U Sedmi Švábů': u'Kopečná 37',
            u'Zábrdovický kostel': u'Zábrdovická 1',
            u'Kartouzský klášter': u'Božetěchova 2',
            u'Jakubská kostnice': u'Jakubské náměstí',
            u'Františkánský klášter': u'Františkánská',
            u'pod Bílou horou': u'Slatinská',
            u'Rosické nádraží': u''}
    
    # fetch all article urls
    for match in re.finditer(r'href="(http://agartha.cz/[^"]+/brno/[^"]+/)index.php">([^<]+)', Downloader('http://agartha.cz/html/pruzkumy/brno/').text('cp1250')):
        title = match.group(2).strip()
        url = match.group(1)
        
        log('article', title)
    
        # determining location
        location = re.sub(r'\s+\W?\w\W?\s+', ' ', title).strip() # strip one-char words 
        if '-' in location:
            location = title.split('-')[0].strip()
    
        geocoded = None
        while len(location) and not geocoded:
            if location in BIAS:
                # some locations need manual hinting :(
                location = BIAS[location]
            
            log('location', location)
            geocoded = Geocoder(location).fetch()
            if not geocoded:
                # remove last word and try again
                location = re.sub(r'[^\s]+$', '', location).strip()
        
        if geocoded:
            log('geocoded', 'yes')
            
            place_id = db.insert_update('places', geocoded)
            article_id = db.insert_update('articles', {'title': title, 'url': url, 'source_id': source_id})
            
            # save relations
            db.insert_update('has_tag', {'place_id': place_id, 'tag_id': tag_id}, last_id=False)
            db.insert_update('is_about', {'place_id': place_id, 'article_id': article_id}, last_id=False)
            
            db.commit()
        

        
if __name__ == '__main__':
    run()
    
    
    