#-*- coding: utf-8 -*-
from threading import Lock, Thread
import threading
import time
import random
import sqlite3
from Queue import Queue
from tools import *

class Item():
	"""deep记录每个url到第几层了"""
	def __init__(self, url, deep):
		self.url = url
		self.deep = deep

class UrlQueue():
	"""放待处理的url的队列，todo
	表示还剩多少没处理，done表示已经处理完的"""
	def __init__(self):
		from tools import Argument
		global Argument
		self.sheet_lock = Argument['sheet_lock']
		self.sheet_url = Argument['sheet_url']
		self.logs = Argument['logging']
		self.queue = Queue()
		self.done = 0
		self.todo = 0

	def push(self, item):
		"""将项目放入队列，线程安全"""
		self.sheet_lock.acquire()
		if item.url not in self.sheet_url:
			self.logs.info('pushed[%s] deep[%s]', item.url, item.deep)
			self.queue.put(item)
			self.sheet_url.add(item.url)
		self.todo += 1
		self.sheet_lock.release()

	def pop(self):
		"""将项目弹出队列，线程安全"""
		try:
			item = self.queue.get(block=True, timeout=30) # 如果60秒内没有新的url，则退出线程
		except:
			return None
		self.logs.info('consumed[%s] deep[%s]', item.url, item.deep)
		self.sheet_lock.acquire()
		self.done += 1
		self.sheet_lock.release()
		return item


class ParseUrlThread(Thread):
	"""线程既是生产者，也是消费者"""
	def __init__(self):
		super(ParseUrlThread, self).__init__()
		self.url_queue = Argument['url_queue']
		self.logs = Argument['logging']

	def run(self):
		global Argument
		self.connector = sqlite3.connect(Argument['dbfile']) # 每个线程自己独立的数据库链接
		self.logs.info("Created connection to sqlite3:%s", self.connector)
		while True:
			item = self.url_queue.pop()
			if not item: # 如果在一定时间内消费完，则退出
				self.logs.info('All consumed, finished')
				break
			if item.deep > int(Argument['deep']):
				continue
			url_list = parse(item.url, self.connector)
			for url in url_list:
				item_new = Item(url, item.deep+1)
				self.url_queue.push(item_new)
		self.connector.close()
		return
