#-*- coding: utf-8 -*-
from __future__ import with_statement
import sqlite3
from contextlib import closing

class Table():
	def __init__(self, dbfile, log):
		self.connector = sqlite3.connect(dbfile)
		self.connector.text_factory = str
		self.logs = log

	def __del__(self):
		self.connector.close()

	def create_page(self):
		"""建表"""
		with closing(self.connector.cursor()) as cursor:
			cursor.execute("create table if not exists page (id integer primary key AutoIncrement, content text)")
			self.connector.commit()
			self.logs.info("Create table succed")

	def insert_page(self, data):
		"""插入条目"""
		values = (data,)
		with closing(self.connector.cursor()) as cursor:
			cursor.execute("insert into page(content) values(?)", values)
			self.connector.commit()
			self.logs.info("Insert one row")

	def query_page(self):
		"""查询数据库数据条数"""
		with closing(self.connector.cursor()) as cursor:
			cursor.execute("select count(*) from page")
			res = cursor.fetchone()
			logs.info("Total count [%s]", res[0])

