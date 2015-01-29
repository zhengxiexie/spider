# -*- coding: utf-8 -*-
from Queue import Queue
import logging


class Item():
    """deep记录每个url到第几层了"""

    def __init__(self, url, deep):
        self.url = url
        self.deep = deep


class UrlQueue():
    """放待处理的url的队列，todo 表示还剩多少没处理，
       done表示还 剩多少没处理 示已经处理完的
    """

    def __init__(self, sheet_lock, sheet_url):
        self.sheet_lock = sheet_lock
        self.sheet_url = sheet_url
        self.queue = Queue()
        self.pushed = 0
        self.popped = 0

    def push(self, item):
        """将项目放入队列，线程安全"""
        logging.debug('waiting')
        self.sheet_lock.acquire()
        if item.url not in self.sheet_url:
            logging.info('pushed[%s] deep[%s]', item.url, item.deep)
            self.queue.put(item)
            self.sheet_url.add(item.url)
            self.pushed += 1
            logging.debug('pushed:%s', self.pushed)
        self.sheet_lock.release()

    def pop(self):
        """将项目弹出队列，线程安全"""
        try:
            # 如果5秒内没有新的url，则退出线程
            item = self.queue.get(block=True, timeout=5)
            logging.debug('waiting')
            self.sheet_lock.acquire()
            self.popped += 1
            logging.debug('popped:%s', self.popped)
            self.sheet_lock.release()
            logging.info('consumed[%s] deep[%s]', item.url, item.deep)
        except:
            return None
        logging.debug(item.url)
        return item
