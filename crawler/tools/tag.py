#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tag management."""



from tools.database import Database
from tools import slugify



class InvalidTagError(ValueError):
    pass
    
class Tag(object):
    
    HIERARCHY = {'nonsmoking': {'name': u'Nekuřácké podniky',
                                'tags': [('non-smoking', u'nekuřácký podnik')]},
                 
                 'beer': {'name': u'Pivo',
                          'tags': []}, # dynamic, beer brand names
                 
                 'wifi': {'name': u'Wi-Fi',
                          'tags': [('free-wifi', u'Wi-Fi zdarma')]},
                 
                 'grunge': {'name': u'Podzemní a tajuplná místa',
                            'tags': [('kafelanka', u'Kafélanka'),
                                     ('former-kafelanka', u'zaniklá Kafélanka'),
                                     ('underground', u'podzemí'),
                                     ('agartha-research', u'průzkum Agartha')]},
                 
                 'info': {'name': u'Články a tipy',
                          'tags': []}} # beware! tags are related to PLACES, not to ARTICLES
    
    def __init__(self, slug):
        self.db = Database()
        tag_id = self._find_tag(slug)

        if not tag_id:
            raise InvalidTagError()
        self.id = tag_id
    
    def _find_tag(self, slug):
        tag_id = None
        for category_slug, category in Tag.HIERARCHY.items():
            for tag_slug, tag_name in category['tags']:
                if slug == tag_slug:
                    category_id = self.db.insert_update('category', {'name': category['name'], 'slug': category_slug})
                    tag_id = self.db.insert_update('tag', {'name': tag_name, 'slug': tag_slug, 'category_id': category_id})
                    break
        self.db.commit()
        return tag_id
    
    def get_id(self):
        return self.id



class BeerTag(Tag):
    
    _CACHE = {}
    
    _CATEGORY_ID = None
    
    def __init__(self, beer_name):
        super(BeerTag, self).__init__(beer_name)
    
    def _find_tag(self, beer_name):
        slug = slugify(beer_name)
        
        if not BeerTag._CATEGORY_ID:
            BeerTag._CATEGORY_ID = self.db.insert_update('category', {'name': Tag.HIERARCHY['beer']['name'], 'slug': 'beer'});
        if slug in BeerTag._CACHE:
            tag_id = BeerTag._CACHE[slug]
        else:
            tag_id = self.db.insert_update('tag', {'name': beer_name, 'slug': slug, 'category_id': BeerTag._CATEGORY_ID})
            BeerTag.CACHE[slug] = tag_id
            Tag.HIERARCHY['beer']['tags'].append((slug, beer_name))
        self.db.commit()
        return tag_id


