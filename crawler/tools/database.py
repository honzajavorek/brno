#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Database tools."""



from MySQLdb.cursors import DictCursor
import MySQLdb as db
from datetime import datetime
import warnings



class Database(object):
    
    def __init__(self):
        self.conn = db.connect(
            host='localhost',
            user='dev',
            passwd='dev',
            db='brno',
            charset='utf8',
        )
        warnings.filterwarnings('error', category=db.Warning)
        self.insert_id = None
    
    def execute(self, sql, params=None):
        cursor = self.conn.cursor(DictCursor)
        cursor.execute(sql, params)
        self.insert_id = self.conn.insert_id()
        return cursor
    
    def _prepare_values(self, data):
        values = []
        for _, value in data.items():
            # handle datetimes
            if isinstance(value, datetime):
                value = value.isoformat(' ')
            elif isinstance(value, basestring):
                value = unicode(value)
            values.append(value)
        return values

    def query(self, sql, params=None):
        cursor = self.execute(sql, params)
        return cursor.fetchall()
    
    def insert_update(self, table, data, last_id=True):
        # see http://stackoverflow.com/questions/589284/imploding-a-list-for-use-in-a-python-mysqldb-in-clause/589416#589416
        sql = 'INSERT INTO %s ('
        last_id = ', id = LAST_INSERT_ID(id)' if last_id else ''
        insert_format_strings = ', '.join(['%s'] * len(data))
        sql += insert_format_strings + ') VALUES (%s) ON DUPLICATE KEY UPDATE %s' + last_id

        # format INSERT statement
        columns = data.keys()
        values = self._prepare_values(data)

        # format UPDATE statement
        update_format_strings = []
        for key in data.keys():
            update_format_strings.append(key + ' = %s')
        update_format_strings = ', '.join(update_format_strings)

        sql = sql % ((table,) + tuple(columns) + (insert_format_strings,) + (update_format_strings,))
        params = tuple(values) + tuple(values)

        self.execute(sql, params)
        if last_id:
            return self.insert_id
    
    def commit(self):
        self.conn.commit()
    
    def __del__(self):
        if self.conn:
            self.conn.close()

