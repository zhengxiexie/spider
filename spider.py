# -*- coding: utf-8 -*-
import logging
import datetime
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
from threading import Lock
from thread_module import *
from url_queue import *
from table import *


def main():

    argument = get_opt()  # 解析命令行参数
    if not argument:
        sys.exit(0)

    sheet_lock = Lock()  # 互斥锁
    sheet_url = set([])  # 已经解析的名单, 防止重复解析

    # 设置日志信息
    level_map = {
        '1': logging.CRITICAL,
        '2': logging.ERROR,
        '3': logging.WARNING,
        '4': logging.INFO,
        '5': logging.DEBUG
    }

    date_format = "%H:%M:%S"
    log_name = argument['logfile']
    log_level = level_map[argument['loglevel']]
    log_format = "[%(asctime)s %(levelname)s %(filename)s:" \
                 "%(lineno)d %(thread)d] %(message)s"

    logging.basicConfig(level=log_level,
            format=log_format,datefmt=date_format,filename=log_name)

    # 建表
    table = Table(argument['dbfile'])
    table.create_page()
    count_before = table.query_page()  # 初始条数
    time_before = datetime.datetime.now()  # 初始时间

    # 生成消息队列
    url_queue = UrlQueue(sheet_lock, sheet_url)

    # 将第一个url入队列
    item = Item(argument['url'], 0)
    url_queue.push(item)

    threads = []

    # 消费者线程
    print 'You start %s consume threads, specify %s depth, key word is %s.' %\
        (int(argument['thread']), int(argument['deep']), argument['key'])

    for i in range(int(argument['thread'])):
        t = ParseUrlThread(url_queue, argument)
        threads.append(t)
        t.start()

    # 打印线程
    p = ProgressThread(url_queue)
    threads.append(p)
    p.start()

    for t in threads:
        t.join()

    count_after = table.query_page()  # 最终条数
    time_after = datetime.datetime.now()  # 结束时间
    print "\nTotal insert count %s this time, spent %s seconds." %\
        ((count_after-count_before), (time_after-time_before).seconds)


if __name__ == "__main__":
    main()
