#!/usr/bin/env python
#-*- coding: utf-8 -*-
# 关于订阅的相关的接口
from header import *
from threading import Lock


class Item():
	"""deep记录每个url到第几层了"""
	def __init__(self, url, deep):
		self.url = url
		self.deep = deep + 1

class UrlQueue():
	"""放待处理的url的队列，todo
	表示还剩多少没处理，done表示已经处理完的"""
	def __init__(self):
		self.queue = Queue()
		self.done = 0
		self.todo = 0

	def push(self, item):
		"""线程安全"""
		print 'push item'
		self.queue.put(item)
		self.todo += 1

	def pop(self):
		"""线程安全"""
		item = self.queue.get()
		self.queue.task_done()
		self.done += 1
		return item

url_queue = UrlQueue()
sheet_lock = Lock()

class ParseUrlThread(Thread):
	def __init__(self):
		super(ParseUrlThread, self).__init__()

	def run(self):
		global url_queue
		nums = range(5)
		while True:
			item = url_queue.pop()
			print 'thread %s consumed' % threading.current_thread().name, item.url
			if item.deep > 3:
				break
			url_list = parse(item.url)
			for url in url_list:
				item = Item(url, item.deep+1)
				url_queue.push(item)
				print 'thread %s pushed' % threading.current_thread().name, url
			time.sleep(random.random())
		return
