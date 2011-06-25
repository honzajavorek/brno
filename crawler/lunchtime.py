#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Crawles over lunchtime.cz."""



from BeautifulSoup import BeautifulSoup
from tools import log, slugify
from tools.database import Database
from tools.downloader import Downloader
from tools.geocoder import Geocoder
import re



# connect to db
db = Database()
source_id = db.insert_update('sources', {'url': 'http://www.lunchtime.cz'})

# prepare
url = 'http://www.lunchtime.cz/restaurace-v-okoli/?q=&city=Brno&lat=49.2&lng=16.616667&zoom=11&latDiff=0.08&lngDiff=0.1'
r_coords = re.compile(r'GMarker\(\s+new GLatLng\(([^,]+),([^\)]+)\),\s+{title:"([^"]+)"[^{]+{fce3\("([^"]+)"')
contents = Downloader(url).text()
html = BeautifulSoup(contents, convertEntities=BeautifulSoup.HTML_ENTITIES)

# get all coords from the map
places = {}
for coords in r_coords.finditer(re.sub(r'[\s\n\r]+', ' ', contents)):
    name = coords.group(3)
    log('coords', name)
    
    geocoded = Geocoder(','.join((coords.group(1), coords.group(2))), resolve_coords=False).fetch()
    geocoded['name'] = name
    
    url = 'http://www.lunchtime.cz%s' % coords.group(4)
    
    places[url] = {'geocoded': geocoded, 'tags': []}

# get links to interesting categories
links = {}

r_wifi = re.compile(r'/restaurace-v-okoli/__wi-fi/')
r_nonsmoking = re.compile(r'/restaurace-v-okoli/__nekuracka-cast/')
r_beer = re.compile(r'/restaurace-v-okoli/_([^_]+)_/')

for box in html.findAll(attrs='filterbox'):
    # wifi
    link = box.find(lambda el: el.name == 'a' and r_wifi.match(el['href']))
    if link:
        log('wifi', 'yes')
        links[u'wi-fi'] = 'http://www.lunchtime.cz%s' % link['href']
    
    # nonsmoking
    link = box.find(lambda el: el.name == 'a' and r_nonsmoking.match(el['href']))
    if link:
        log('nonsmoking', 'yes')
        links[u'nekuřácké'] = 'http://www.lunchtime.cz%s' % link['href']
        
    # beers
    for link in box.findAll(lambda el: el.name == 'a' and r_beer.match(el['href'])):
        name = link.string
        log('beer', name)
        links[name] = 'http://www.lunchtime.cz%s' % link['href']

# process interesting categories
r_place = re.compile(r'href="(http://www.lunchtime.cz/[^/]+/)#kontakt"')
for tag, url in links.items():
    # save tag
    tag_id = db.insert_update('tags', {'name': tag, 'slug': slugify(tag)})
    
    # find all place urls
    log('tag', tag)
    i = 0
    for match in r_place.finditer(Downloader(url).text()):
        place_url = match.group(1)
        if place_url in places:
            # give them the right tags
            places[place_url]['tags'].append(tag_id)
            i += 1
    log('places', i)
            

# finalize, save places and tags
for url, place in places.items():
    name = place['geocoded']['name']
    log('saving', name)
    place_id = db.insert_update('places', place['geocoded'])
    
    for tag_id in place['tags']:
        db.insert_update('has_tag', {'place_id': place_id, 'tag_id': tag_id}, last_id=False)
    
    article_id = db.insert_update('articles', {'title': name, 'url': url, 'source_id': source_id})
    db.insert_update('is_about', {'place_id': place_id, 'article_id': article_id}, last_id=False)
    
    db.commit()
        
            
    