#-*- coding: utf-8 -*-
from threading import Lock
from thread_module import *
from url_queue import *
from table import *
import logging

def main():
	argument = get_opt() # 解析命令行参数
	if not argument:
		return

	sheet_lock = Lock() # 互斥锁
	sheet_url = set([]) # 已经解析的名单, 防止重复解析

	# 设置日志信息
	level_map = {'1':logging.CRITICAL, '2':logging.ERROR, '3':logging.WARNING, '4':logging.INFO,
			'5':logging.DEBUG}
	logging.basicConfig(level = level_map[argument['loglevel']],
						format = "[%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(thread)d] %(message)s",
						datefmt="%H:%M:%S", filename=argument['logfile'])
	# 建表
	table = Table(argument['dbfile'], logging)
	table.create_page()

	# 生成消息队列
	url_queue = UrlQueue(sheet_lock, sheet_url, logging)

	# 将第一个url入队列
	item = Item(argument['url'], 0)
	url_queue.push(item)

	threads = []

	# 消费者线程
	for i in range(int(argument['thread'])):
		t = ParseUrlThread(url_queue, logging, argument['dbfile'], int(argument['deep']), argument['key'])
		threads.append(t)
		t.start()

	# 打印线程
	p = ProgressThread(url_queue)
	threads.append(p)
	p.start()

	for t in threads:
		t.join()

	table.query_page()

if __name__ == "__main__":
	main()
