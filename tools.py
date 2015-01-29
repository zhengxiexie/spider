# -*- coding: utf-8 -*-
import re
import urllib2
import getopt, sys
import logging


def get_data(url):
    """抓取网页"""
    html = ''
    logging.debug(html)
    try:
        response = urllib2.urlopen(url, timeout=1)
        header = response.info().getheader('Content-Type')
        if 'text/html' in header:  #只下载文本内容
            html = response.read()
    except:
        return html
    logging.debug(html)
    return html


def parse(table, url, key):
    """解析当前页面的所有url, 如果符合key的页面，则入库"""
    url_list = []
    data = get_data(url)
    logging.debug(data)
    if key in data:
        table.insert_page(data)
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
    """解析命令行参数"""
    argu_map = {
         "-u": "url",
         "-d": "deep",
         "-f": "logfile",
         "-l": "loglevel",
         "--thread": "thread",
         "--dbfile": "dbfile",
         "--key": "key"
    }

    argument = {
         "url": "http://www.baidu.com",
         "deep": "2",
         "logfile": "./log",
         "loglevel": "2",
         "thread": "3",
         "dbfile": "./sqlite",
         "key": "html"
    }

    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:d:f:l:", ["help", "thread=", "dbfile=", "key="])
        for o, a in opts:
            if o == "--help":
                detail_usage()
                return None
            elif a:
                argument[argu_map[o]] = a
        return argument

    except getopt.GetoptError:
        usage()
        return None
