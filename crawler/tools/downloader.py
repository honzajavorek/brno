#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Simple downloader."""



from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from xml.etree import ElementTree
import json
import urllib
import urllib2



class Downloader(object):
    
    def __init__(self, url, *args):
        if args:
            params = []
            for arg in args:
                params.append(urllib.quote(unicode(arg).encode('utf8')))
            self.url = url % tuple(params)
        else:
            self.url = url
        
    def _fetch(self):
        return urllib2.urlopen(self.url).read()
        
    def text(self, encoding='utf8'):
        return unicode(self._fetch(), encoding)
    
    def json(self):
        return json.loads(self._fetch())
    
    def xml(self, soup=False):
        response = self._fetch()
        if soup:
            return BeautifulStoneSoup(response, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
        return ElementTree.XML(response)
    
    def html(self):
        return BeautifulSoup(self._fetch(), convertEntities=BeautifulSoup.HTML_ENTITIES)


