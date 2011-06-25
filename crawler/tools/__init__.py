#!/usr/bin/python
# -*- coding: utf-8 -*-
"""General handy tools."""



import re
import unicodedata



def log(type, text):
    print '[%s] %s' % (type, text)



def slugify(value):
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub(r'[^\w\s-]', '', value).strip().lower())
    return re.sub(r'[-\s]+', '-', value)



def _decode_unicode_entities_callback(matches):
    id = matches.group(1)
    try:
        return unichr(int(id))
    except:
        return id

def decode_unicode_entities(string):
    if '&#' in string:
        return re.sub(r'&#(\d+)(;|(?=\s))', _decode_unicode_entities_callback, string)
    return string
