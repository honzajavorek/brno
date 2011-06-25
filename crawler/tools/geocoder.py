#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Geocoder."""



from tools.downloader import Downloader
import re



class Geocoder(object):
    
    BOUNDS = (('49.104', '16.423'), ('49.316', '16.762'))
    
    GOOGLE_URL = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&region=cz&language=cs&sensor=false'
    
    SEZNAM_URL = 'http://beta.api.mapy.cz/geocode?query=%s'
    
    def __init__(self, query, resolve_coords=True):
        self.resolve_coords = resolve_coords
        if not query:
            self.query = None
        else:
            self.query = query
            if not self._is_coords(query):
                self.query += ', brno, czech republic'
    
    def _normalize_coord(self, coord):
        return str(round(float(coord), 5))
    
    def _is_coords(self, query):
        return re.match(r'\s*\d+\.\d+\s*,\s*\d+\.\d+', query)
    
    def _is_in_bounds(self, lat, lng):
        lat = float(lat)
        lng = float(lng)
        return lat > float(Geocoder.BOUNDS[0][0]) \
            and lat < float(Geocoder.BOUNDS[1][0]) \
            and lng > float(Geocoder.BOUNDS[0][1]) \
            and lng < float(Geocoder.BOUNDS[1][1])
    
    def fetch(self):
        if not self.query:
            return None
        
        # returning coords
        if not self.resolve_coords and self._is_coords(self.query):
            lat, lng = self.query.split(',')
            return {'lat': self._normalize_coord(lat.strip()),
                    'lng': self._normalize_coord(lng.strip()),
                    'name': None,
                    'address': None}
            
        # bounding
        bounds = '&bounds=%s|%s' % tuple([','.join(coords) for coords in Geocoder.BOUNDS])
        bounded_url = Geocoder.GOOGLE_URL + bounds
        
        # fetching from Google
        data = Downloader(bounded_url, self.query).json()

        if data.get('status', '') == 'OK' \
            and data['results'][0]['address_components'][0]['long_name'] != 'Brno':
            
            coords = data['results'][0]['geometry']['location']
            lat = self._normalize_coord(coords['lat'])
            lng = self._normalize_coord(coords['lng'])
            name = data['results'][0]['address_components'][0]['long_name']
            address = data['results'][0]['formatted_address']
            
            if self._is_in_bounds(lat, lng):
                return {'lat': lat, 'lng': lng, 'name': name, 'address': address}
        
        # fetching from Seznam
        data = Downloader(Geocoder.SEZNAM_URL, self.query).xml()
        for item in data.findall('.//item'):
            lat = self._normalize_coord(item.attrib.get('y'))
            lng = self._normalize_coord(item.attrib.get('x'))
            name = item.attrib.get('title')
            
            if self._is_in_bounds(lat, lng):
                return {'lat': lat, 'lng': lng, 'name': name, 'address': None}
        
        return None


        