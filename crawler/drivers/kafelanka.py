#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Crawles over kafelanka.cz."""



from tools import log
from tools.database import Database
from tools.downloader import Downloader
from tools.geocoder import Geocoder
from tools.tag import Tag
import re



def run():
    # connect to db
    db = Database()
    source_id = db.insert_update('sources', {'url': 'http://www.kafelanka.cz'})
    
    # prepare
    r_coord = re.compile(ur'mista\[\d+\]\s*=\s*new Array\(([\d\-\.]+),\s+([\d\-\.]+),([^,]+), "([^"]+)", "([^"]+)", "([^"]+)"\);')
    
    place_tag_id = Tag('kafelanka').get_id()
    former_place_tag_id = Tag('former-kafelanka').get_id()
    
    # fetch all article urls
    for match in re.findall(r'href="(mapa\.php\?ceho=[^"]+)"', Downloader('http://kafelanka.wz.cz/mista/').text('cp1250')):
        log('map', match)
        url = 'http://kafelanka.cz/mista/%s' % match
        html = Downloader(url).text('cp1250')
        
        for data in r_coord.finditer(html):
            log('place', data.group(4))
            
            tag_ids = [place_tag_id]
            if data.group(3).strip(', "\'') == 'neni':
                tag_ids.append(former_place_tag_id)
            
            lat = str(float(data.group(1)))
            lng = str(float(data.group(2)))
            
            name = data.group(4)
            
            geocoded = Geocoder(','.join((lat, lng)), resolve_coords=False).fetch()
            geocoded['name'] = name
            
            article_url = 'http://kafelanka.cz/mista/%s' % data.group(5)
            photo_url = 'http://kafelanka.cz/mista/foto/%s' % data.group(6)
            
            place_id = db.insert_update('places', geocoded)
            article_id = db.insert_update('articles', {'title': name, 'url': article_url, 'photo_url': photo_url, 'source_id': source_id})
            
            # save relations
            for id in tag_ids:
                db.insert_update('has_tag', {'place_id': place_id, 'tag_id': id}, last_id=False)
            db.insert_update('is_about', {'place_id': place_id, 'article_id': article_id}, last_id=False)
            
            db.commit()
        
        break # apparently, all places are listed on every page
        

        
if __name__ == '__main__':
    run()
    
    
    