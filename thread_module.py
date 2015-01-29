# -*- coding: utf-8 -*-
import time
import logging
from threading import Thread
import threading
from url_queue import Item
from tools import *
from table import *


class ParseUrlThread(Thread):
    """线程既是生产者，也是消费者"""

    def __init__(self, url_queue, data_queue, argument):
        super(ParseUrlThread, self).__init__()
        self.url_queue = url_queue
        self.data_queue = data_queue
        self.deep = int(argument['deep'])
        self.key = argument['key']

    def run(self):
        while True:
            item = self.url_queue.pop()
            if not item:  # 如果在一定时间内消费完，则退出
                logging.info('All consumed, finished')
                break
            logging.debug(self.key)
            url_list = parse(item.url, self.key, self.data_queue)
            for url in url_list:
                if item.deep >= self.deep:  # 如果url深度等于大于自定义深度，则不入队列
                    continue
                item_new = Item(url, item.deep + 1)
                self.url_queue.push(item_new)
        return

class DBThread(Thread):
    """单线程将数据入库, 多线程操作sqlite容易出现lock问题"""

    def __init__(self, data_queue, dbpath):
        super(DBThread, self).__init__()
        self.data_queue= data_queue
        self.dbpath = dbpath
        self._stop = False

    def stop(self):
        self._stop = True

    def stopped(self):
        return self._stop

    def run(self):
        self.table = Table(self.dbpath)
        while True:
            if self.stopped():
                del self.table
                return
            try:
                data = self.data_queue.get(block=True, timeout=5)
            except:
                continue
            self.table.insert_page(data)
        return

class ProgressThread(Thread):
    """每隔10s打印进度信息, 读信息无需上锁"""

    def __init__(self, url_queue):
        super(ProgressThread, self).__init__()
        self.url_queue = url_queue
        self._stop = False

    def stop(self):
        self._stop = True

    def stopped(self):
        return self._stop

    def run(self):
        time.sleep(5)  # 防止开始进度显示100%
        while True:
            if self.stopped():
                return
            pushed = float(self.url_queue.pushed)
            popped = float(self.url_queue.popped)
            info = 'pushed:%s popped:%s' % (int(pushed), int(popped))
            percent = int((popped / pushed) * 100)
            sys.stdout.write("\r" + str(percent) + '% ||' + '-> ' + info + "    ")
            sys.stdout.flush()
            time.sleep(0.1)
        return
