# -*- coding: utf-8 -*-
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
            if not item:  # 如果在一定时间内消费完，则退出
                self.logs.info('All consumed, finished')
                break
            self.logs.debug(self.key)
            url_list = parse(table, item.url, self.key, self.logs)
            for url in url_list:
                if item.deep > self.deep:  # 如果url深度超过某值，则不入队列
                    continue
                item_new = Item(url, item.deep + 1)
                self.url_queue.push(item_new)
        return


class ProgressThread(Thread):
    """每隔10s打印进度信息, 读信息无需上锁"""

    def __init__(self, url_queue):
        super(ProgressThread, self).__init__()
        self.url_queue = url_queue

    def run(self):
        count = 0  # 如果pushed=popped，则循环再检查10次，以防进度还没显示100%，就退出
        time.sleep(10)  # 防止开始进度显示100%
        while True:
            if count > 10:
                break
            pushed = float(self.url_queue.pushed)
            popped = float(self.url_queue.popped)
            info = 'pushed:%s popped:%s' % (int(pushed), int(popped))
            percent = int((popped / pushed) * 100)
            sys.stdout.write("\r" + str(percent) + '% ||' + '-> ' + info + "    ")
            sys.stdout.flush()
            time.sleep(0.1)
            if self.url_queue.pushed == self.url_queue.popped:
                count += 1
        return
