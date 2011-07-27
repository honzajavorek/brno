#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Crawles over podzemi.brno.cz."""



from tools import log
from tools.database import Database
from tools.downloader import Downloader
from tools.geocoder import Geocoder
from tools.tag import Tag
import re



def run():
    # connect to db
    db = Database()
    source_id = db.insert_update('sources', {'url': 'http://www.podzemi.brno.cz'})
    
    # prepare
    tag_id = Tag('underground').get_id()
    
    BIAS = {u'Kolektory': u'',
            u'Primární': u'',
            u'Sekundární': u'',
            u'Kanalizace': u'',
            u'Historie': u'',
            u'Současnost': u'',
            u'Vodovody': u'',
            u'Historické podzemí': u'',
            u'Úvod': u'',
            u'Aktuality': u'',
            u'Fotogalerie': u'',
            u'Kontakt': u'',
            u'Římské náměstí': u'Františkánská'}
    
    # fetch all locations
    for a in Downloader('http://www.podzemi.brno.cz').html().find(attrs={'id': 'obsahy-obsah'}).find('td').findAll('a'):
        title = re.sub(r'\s+', ' ', a.string).strip()
        url = a['href']
        
        log('article', title)
    
        # determining location
        location = title
        if location in BIAS:
            # some locations need manual hinting...
            location = BIAS[location]
        geocoded = Geocoder(location).fetch()
        
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
    
    
    