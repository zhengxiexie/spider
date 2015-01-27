#-*- coding: utf-8 -*-
from module import *
from tools import *


def main():
	"""主程序"""

	# 初始化环境
	Argument = init_context()

	logs = Argument["logging"]
	logs.info("Parsed arguments: %s", str(Argument))

	threads = []
	for i in range(int(Argument['thread'])):
		t = ParseUrlThread()
		threads.append(t)
		t.start()

	for t in threads:
		t.join()

	query_page()

if __name__ == "__main__":
	main()
