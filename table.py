# -*- coding: utf-8 -*-
from __future__ import with_statement
import sqlite3
import traceback
from contextlib import closing
import logging


class Table():
    """sqlite3数据库操作相关"""

    def __init__(self, dbfile):
        self.connector = sqlite3.connect(dbfile)
        self.connector.text_factory = str
        self.cursor = self.connector.cursor()

    def __del__(self):
        self.cursor.close()
        self.connector.close()

    def create_page(self):
        """建表"""
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS page (id INTEGER "\
                           "PRIMARY KEY AUTOINCREMENT, content TEXT)")
            self.connector.commit()
            logging.info("Create table succed")
        except Exception, e:
            logging.error(e)

    def insert_page(self, data):
        """插入条目"""
        values = (data,)
        try:
            self.cursor.execute("INSERT INTO page(content) VALUES(?)", values)
            self.connector.commit()
            logging.info("Insert one row")
        except Exception, e:
            logging.error(e)

    def query_page(self):
        """查询数据库数据条数"""
        try:
            self.cursor.execute("SELECT count(*) FROM page")
            res = self.cursor.fetchone()
            logging.info("Total count [%s]", res[0])
        except Exception, e:
            logging.error(e)
