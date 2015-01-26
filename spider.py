from header import *
from module import *
from tools import *
from macro import *
from threading import Lock

url_queue = UrlQueue()
sheet_lock = Lock()

item = Item("www.youku.com", 0)

url_queue.push(item)

threads = []
for i in range(5):
	t = ParseUrlThread()
	threads.append(t)
	t.start()

for t in threads:
	t.join()
