#-*- coding: utf-8 -*-
from threading import Thread
from url_queue import Item
from tools import *
from table import *
import time

class ParseUrlThread(Thread):
	"""线程既是生产者，也是消费者"""
	def __init__(self, url_queue, logging, dbpath, deep, key):
		super(ParseUrlThread, self).__init__()
		self.url_queue = url_queue
		self.logs = logging
		self.dbpath = dbpath
		self.deep = deep
		self.key = key

	def run(self):
		table = Table(self.dbpath, self.logs)
		while True:
			item = self.url_queue.pop()
			if not item: # 如果在一定时间内消费完，则退出
				self.logs.info('All consumed, finished')
				break
			if item.deep > self.deep:
				continue
			url_list = parse(table, item.url, self.key)
			for url in url_list:
				item_new = Item(url, item.deep+1)
				self.url_queue.push(item_new)
		return

class ProgressThread(Thread):
	"""每隔10s打印进度信息, 读信息无需上锁"""
	def __init__(self, url_queue):
		super(ProgressThread, self).__init__()
		self.url_queue = url_queue

	def run(self):
		while True:
			time.sleep(1)
			print 'todo:%s done:%s\n' % (self.url_queue.todo, self.url_queue.done)
			if self.url_queue.todo == self.url_queue.done:
				break
		return
