import re
import urllib2

def get_data(url):
	try:
		print 'here'
		response = urllib2.urlopen(url, timeout=10)
		print response
		html = response.read()
		return html
	except:
		return ''

def parse(url):
	url_list = []
	data = get_data(url)
	print data
	res_iter = re.finditer(r'href="(.*?)"', data, re.S)
	for i in res_iter:
		url = i.group(1)
		url_list.append(url)
	return url_list
