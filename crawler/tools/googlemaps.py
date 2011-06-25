#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Google Maps."""



import re
import urllib



class GoogleMaps(object):
    
    def parse_link_url(self, url):
        querystring = re.sub(r'^[^\?]+\?', '', url)
        for param in querystring.split('&'):
            key, value = param.split('=')
            if key == 'q':
                # http://stackoverflow.com/questions/5139249/python-url-unquote-unicode
                return urllib.unquote_plus(value.encode('ascii')).decode('utf8')


        