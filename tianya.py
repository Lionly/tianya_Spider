#-*- coding: utf-8 -*-
# 获取天涯的帖子内容

import os
import sys
import glob
import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool

# 调整中文输出
class UnicodeStreamFilter:
    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding
    def write(self, s):
        if type(s) == str:
            s = s.decode("utf-8")
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)
if sys.stdout.encoding == 'cp936':
    sys.stdout = UnicodeStreamFilter(sys.stdout)

def geturl():
	loop = True
	while loop:
		url = raw_input(u'请输入天涯帖子链接(任意页)：')
		index1, index2 = url.rfind('-'), url.rfind('.')
		if  (url[0:21] == 'http://bbs.tianya.cn/') and (url[-6:] == url_px) and index1>0 and index2>0:
			url_base, start_page = url[0:index1+1], int(url[index1+1:index2])
			loop = False
			return url, url_base, start_page
		else:
			print u'输入的链接不完整，或者格式不对\n'
def getpages(maxpage):
	loop = True
	while loop:
		page = raw_input(u'请输入待整理的页数（建议不要大于 100）：')
		page = int(page)
		if page<0 or page>100:
			print u'输入的页数不正确，或者大于 100\n'
		else:
			end_page = start_page + page
			if maxpage+1 < end_page:
				print u'输入的页数超出当前帖子最大页数\n'
			else:
				print '准备完毕，即将开始...\n开始页：'+str(start_page)+'\n结束页：'+str(end_page-1)
				loop = False
				return end_page
def seturl(info, i):
	return info[0]+str(i)+info[1]
def writeline(fo, str):
	fo.write(str+'\n')
def onelayer(content, reply):
	reportme = reply.find('a', class_='reportme a-link')
	if reportme['authorid'] == user_info['uid']:
		return content.get_text("\n", strip=True)+'\n'
	else:
		return False
def writeOnePage(pageno):
	filepath = 'tmp/page_' + str(pageno) + '.txt'
	filehandle = open(filepath,'w')
	writeline(filehandle, '\n')
	soup = BeautifulSoup(requests.get(seturl(url_info, pageno)).content, "html.parser", from_encoding="utf-8" )
	if pageno == 1:
		writeline(filehandle, soup.find('div', class_='atl-item host-item').find('div', class_='bbs-content').get_text("\n", strip=True).encode('utf-8'))
	item_tag = soup.find_all('div', class_='atl-item')
	item_count = 0
	for child in item_tag:
		content = child.find('div', class_='bbs-content')
		reply = content.find_next_sibling('div', class_='atl-reply')
		if reply is None:
			print 'none'
		else:
			layer = onelayer(content, reply)
			if layer:
				item_count = item_count + 1
				writeline(filehandle, layer.encode('utf-8'))
	filehandle.close()
	if item_count == 0:
		os.remove(filepath)
	print u'处理进度，已完成第', pageno, u'页...'
	pass
if __name__ == '__main__':
	# 1、输入 URL
	start_page, end_page, url_base, url_px = 1, 1, '', '.shtml'
	url, url_base, start_page = geturl()
	url_info = [url_base, url_px]
	# 获取帖子的基本信息
	soup = BeautifulSoup(requests.get(seturl(url_info, 1)).content, "html.parser", from_encoding="utf-8" )
	user_info = soup.find('div', class_='atl-info').find('span').find('a')
	# 获取总页数 没处理小于一页的，可能出错
	maxpage = soup.find('div', class_='atl-pages').find('form').find('a', class_='js-keyboard-next').find_previous_sibling('a')
	base_info = [soup.title.text.split('_')[0], user_info['uname'], user_info['uid']]
	print u'输入的链接解析完毕\n===================\n输入 URL：', url
	print u'帖子标题:', base_info[0]
	print u'帖子作者:', base_info[1], 'UID:', base_info[2]
	print u'当 前 页：', start_page, u'\n帖子总页数:', maxpage.text

	# 2、输入页数，求出 end_page
	end_page = getpages(int(maxpage.text))
	os.mkdir('tmp')

	# 3、多线程(耗时的操作)
	pool = Pool(10)
	pool.map(writeOnePage, range(start_page, end_page))
	pool.close()
	pool.join()

	# 4、整理输出最终结果
	filehandle = open(base_info[0] + '.txt','w')
	writeline(filehandle, base_info[0].encode('utf-8'))
	writeline(filehandle, '作者：'+base_info[1].encode('utf-8'))
	writeline(filehandle, 'URL：'+url.encode('utf-8'))
	writeline(filehandle, '开始页：'+str(start_page)+'\n结束页：'+str(end_page-1).encode('utf-8'))
	for pagefile in glob.glob(r'tmp/page_*.txt'):
		file_object = open( pagefile )
		try:
		    all_the_text = file_object.read()
		    filehandle.write(all_the_text)
		finally:
		    file_object.close()
		    os.remove(pagefile)
	filehandle.close()
	os.rmdir('tmp')
	raw_input(u'全部完成，按回车键结束...')
