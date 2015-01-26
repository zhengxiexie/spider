from module import *
from tools import *


item = Item("http://www.youku.com", 0)

url_queue.push(item)

threads = []
for i in range(5):
	t = ParseUrlThread()
	threads.append(t)
	t.start()

for t in threads:
	t.join()
