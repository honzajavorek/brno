#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Crawles over kafelanka.cz."""



from tools import log, dmsToDec
from tools.database import Database
from tools.downloader import Downloader
from tools.geocoder import Geocoder
import re



def run():
    # connect to db
    db = Database()
    source_id = db.insert_update('sources', {'url': 'http://www.kafelanka.cz'})
    
    # prepare
    r_coord = re.compile(ur'mista\[\d+\]\s*=\s*new Array\("([\d\.]+)°([\d\.]+)\\\'([\d\.])[^"]+"N;\s+([\d\.]+)°([\d\.]+)\\\'([\d\.]+)\\"E", (\d+), "([^"]+)", "([^"]+)", "([^"]+)"\);')
    
    place_tag_id = db.insert_update('tags', {'name': u'Kafélanka', 'slug': 'kafelanka'})
    former_place_tag_id = db.insert_update('tags', {'name': u'zaniklé místo', 'slug': 'zanikle-misto'})
    
    # fetch all article urls
    for match in re.findall(r'href="(mapa\.php\?ceho=[^"]+)"', Downloader('http://kafelanka.wz.cz/mista/').text('cp1250')):
        log('map', match)
        url = 'http://kafelanka.cz/mista/%s' % match
        html = Downloader(url).text('cp1250')
        
        for data in r_coord.finditer(html):
            log('place', data.group(8))
            
            tag_ids = [place_tag_id]
            if data.group(7) == 2:
                tag_ids.append(former_place_tag_id)
            
            lat = str(dmsToDec(data.group(1), data.group(2), data.group(3)))
            lng = str(dmsToDec(data.group(4), data.group(5), data.group(6)))
            
            name = data.group(8)
            
            geocoded = Geocoder(','.join((lat, lng)), resolve_coords=False).fetch()
            geocoded['name'] = name
            
            article_url = 'http://kafelanka.cz/mista/%s' % data.group(9)
            photo_url = 'http://kafelanka.cz/mista/foto/%s' % data.group(10)
            
            place_id = db.insert_update('places', geocoded)
            article_id = db.insert_update('articles', {'title': name, 'url': article_url, 'source_id': source_id})
            
            # save relations
            for id in tag_ids:
                db.insert_update('has_tag', {'place_id': place_id, 'tag_id': id}, last_id=False)
            db.insert_update('is_about', {'place_id': place_id, 'article_id': article_id}, last_id=False)
            
            db.commit()
        
        break # apparently, all places are listed on every page
        

        
if __name__ == '__main__':
    run()
    
    
    