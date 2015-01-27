#-*- coding: utf-8 -*-
import re
import urllib2
import getopt, sys
import logging
import sqlite3
from module import *
from threading import Lock, Thread

Argument = {}

def get_data(url):
	"""抓取网页"""
	html = ''
	opener = urllib2.build_opener()
	try:
		response = opener.open(url)
		html = response.read()
		return html
	except:
		return html

def insert_page(data, connector):
	"""插入条目"""
	global Argument
	logs = Argument['logging']
	connector.text_factory = str
	values = (data,)
	cursor = connector.cursor()
	try:
		cursor.execute("insert into page(content) values(?)", values)
	except:
		logs.error("Insert error")
	cursor.close()

def query_page():
	"""查询数据库数据条数"""
	global Argument
	connector = sqlite3.connect(Argument['dbfile'])
	cu = connector.cursor()
	cu.execute("select count(*) from page")
	res = cu.fetchall()
	logs = Argument['logging']
	logs.info("Total count [%s]", res[0])
	cu.close()
	connector.close()

def create_page():
	"""建表"""
	global Argument
	logs = Argument['logging']
	connector = sqlite3.connect(Argument['dbfile'])
	cu = connector.cursor()
	try:
		cu.execute("create table if not exists page (id integer primary key AutoIncrement, content text)")
	except:
		logs.error("Create table error")
	connector.commit()
	cu.close()
	connector.close()
	logs.info("Created table")


def parse(url, connector):
	"""解析当前页面的所有url, 如果符合key的页面，则入库"""
	global Argument
	url_list = []
	data = get_data(url)
	if Argument['key'] in data:
		insert_page(data, connector)
	res_iter = re.finditer(r'href="(http.*?)"', data, re.S)
	for i in res_iter:
		url = i.group(1)
		url_list.append(url)
	return url_list

def usage():
	"""简短的帮助"""
	print("Usage:%s [-u|-d|-f|-l] [--help|--thread|--dbfile|--key]")

def detail_usage():
	"""详细的帮助"""
	print("-u      : the start url you crawl, default:http://www.baidu.com")
	print("-d      : the depth you crawl, default:2")
	print("-f      : logfile path, default:./log")
	print("-l      : loglevel, default:2, 1-CRITICAL 2-ERROR 3-WARNING 4-INFO 5-DEBUG")
	print("--thread: how many threads you use, default:3")
	print("--dbfile: sqlite file path, default:./sqlite")
	print("--key   : the key word you want to search, default:html")
	print("--help  : print this message")

def get_opt():
	"""解析命令行参数，存入全局变量"""
	# 全局变量
	global Argument
	Argument = {"url":"http://www.baidu.com", "deep":"2", "logfile":"./log", "loglevel":"2",
			"thread":"3", "dbfile":"./sqlite", "key":"html"}
	argu_map = {"-u":"url", "-d":"deep", "-f":"logfile", "-l":"loglevel", "--thread":"thread",
			"--dbfile":"dbfile", "--key":"key"}
	try:
		opts, args = getopt.getopt(sys.argv[1:], "u:d:f:l:", ["help", "thread=", "dbfile=", "key="])
		for o, a in opts:
			if o == "--help":
				detail_usage()
			elif a:
				Argument[argu_map[o]] = a

	except getopt.GetoptError:
		usage()

def init_context():
	"""初始化环境信息，解析命令行参数，生成日志信息, 生成已处理url的名单及锁"""
	global Argument
	# 解析命令行参数
	get_opt()

	# 生成锁
	sheet_lock = Lock()
	sheet_url = set([])
	Argument['sheet_lock'] = sheet_lock
	Argument['sheet_url'] = sheet_url

	# 设置日志信息
	level_map = {'1':logging.CRITICAL, '2':logging.ERROR, '3':logging.WARNING, '4':logging.INFO,
			'5':logging.DEBUG}
	logging.basicConfig(level = level_map[Argument['loglevel']],
						format = "[%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(thread)d] %(message)s",
						datefmt="%H:%M:%S", filename=Argument['logfile'])
	Argument["logging"] = logging

	# 建表
	create_page()

	# 生成消息队列
	from module import UrlQueue
	from module import Item
	url_queue = UrlQueue()
	Argument['url_queue'] = url_queue

	# 将第一个url入队列
	item = Item(Argument['url'], 0)
	url_queue.push(item)
	return Argument
