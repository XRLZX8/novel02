#-*- coding = utf-8 -*-
"""
@author: XRL
@software: PyCharm
@file: test2.py
@time: 2020/8/2 1:43
"""
import urllib.request
import parsel
import re

def askurl(url):

    head = {
        "User-Agent": "Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit/537.36(KHTML, likeGecko) Chrome / 78.0.3904.108 Safari / 537.36"
    }
    request = urllib.request.Request(url=url,headers=head)
    html = ''
    new_html = ''
    response = urllib.request.urlopen(request)
    html = response.read()
    # print(type(html))
    if 'charset=gbk'.lower() in str(html):
        new_html = html.decode('gbk')
    elif 'charset=utf-8'.lower() in str(html):
        new_html = html.decode('utf-8')
    print(new_html)
    return new_html
    # data = parsel.Selector(html)
    # message = data.xpath('//div[@id="content"]/text()').extract()
    # print(message)



if __name__ =='__main__':
    url = 'https://www.biqubao.com/search.php?q=%E9%BB%8E%E6%98%8E%E4%B9%8B%E5%89%91'
    askurl(url)