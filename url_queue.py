#-*- coding: utf-8 -*-
from Queue import Queue

class Item():
	"""deep记录每个url到第几层了"""
	def __init__(self, url, deep):
		self.url = url
		self.deep = deep

class UrlQueue():
	"""放待处理的url的队列，todo
	表示还剩多少没处理，done表示已经处理完的"""
	def __init__(self, sheet_lock, sheet_url, logs):
		self.sheet_lock = sheet_lock
		self.sheet_url = sheet_url
		self.logs = logs
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
			item = self.queue.get(block=True, timeout=3) # 如果30秒内没有新的url，则退出线程
		except:
			return None
		self.logs.info('consumed[%s] deep[%s]', item.url, item.deep)
		self.sheet_lock.acquire()
		self.done += 1
		self.sheet_lock.release()
		return item
