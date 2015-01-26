from header import *
import re

def get_data(url):
	try:
		return urllib2.urlopen(url, timeout=5)
	except:
		return ''

def parse(url):
	url_list = []
	data = get_data(url)
	res_iter = re.finditer(r'href="(.*?)"', data, re.S)
	for i in res_iter:
		url = i.group(1)
		url_list.append(url)
	return url_list
