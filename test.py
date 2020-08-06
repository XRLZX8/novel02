#-*- coding = utf-8 -*-
"""
@author: XRL
@software: PyCharm
@file: test.py
@time: 2020/8/1 22:16
"""

import urllib.request,urllib.response
from bs4 import BeautifulSoup
import parsel
import re
import pymysql
import unicodedata

# baseurl ='https://www.biqubao.com/search.php?q='
# novel_name = urllib.request.quote(input('请输入小说名'))
# full_name = baseurl+novel_name
# print(full_name)

baseurl ='https://www.biqubao.com/'

find_book_name = re.compile(r'<span>(.*)</span>')
find_book_link = re.compile(r'href="(.*)" title=')
find_chapter = re.compile(r'<a href="(.*)">(.*)</a>')
chapter = {}

#-----------
host = 'localhost'
port = 3306
user = 'XRL'
password = 'GTX1070xrl@123'
database = 'novel01'

#-----------

def main():
    chapter = getchapter()
    savechapter(chapter)

def askurl(url):

    head = {
        "User-Agent": "Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit/537.36(KHTML, likeGecko) Chrome / 78.0.3904.108 Safari / 537.36"
    }
    request = urllib.request.Request(url=url,headers=head)
    html = ''
    response = urllib.request.urlopen(request)
    html = response.read()
    if 'charset=gbk'.lower() in str(html):
        new_html = html.decode('gbk')
    elif 'charset=utf-8'.lower() in str(html):
        new_html = html.decode('utf-8')
    # print(html)
    return new_html

def getchapter():
    html1 = ''
    # html1 = askurl(url)
    #使用保存到本地的网页制作
    with open('html/小说搜索——结果.html',encoding='utf-8')as h1:
        html1 = h1.read()

    data = parsel.Selector(html1)
    message1 = data.xpath('//a[@cpos="title"]').extract()
    book_name = re.findall(find_book_name,str(message1))#获取网页中书名
    book_link = re.findall(find_book_link,str(message1))#获取书籍页面链接尾部
    book_url = book_link[0]
    print(book_link)
    print(book_url)
    html2 = ''
    # html2 = askurl(book_url)
    #使用保存到本地的网页制作
    with open('html/黎明之剑最新章节列表_黎明之剑全文阅读 - 笔趣阁.html',encoding='gbk')as h2:
        html2 = h2.read()
    data = parsel.Selector(html2)
    message2 = data.xpath('//dd').extract()
    chapter_list = message2
    chapter_name =[]
    chapter_link =[]
    for i in range(len(chapter_list)):
        chapter_m = re.findall(find_chapter,chapter_list[i])[0]
        chapter_name.append(chapter_m[1])
        chapter_link.append(chapter_m[0])
    chapter=dict(zip(chapter_name,chapter_link))
    # print(chapter)
    # return chapter_name,chapter_link
    return chapter

def savechapter(chapter):

    conn = pymysql.connect(host=host,port=port,user=user,password=password,
                           database=database)
    cur = conn.cursor()
    sql1 = '''
    create table if not exists test_chapter(
    id int not null primary key AUTO_INCREMENT,
    chapter_name varchar(255) not null,
    chapter_link text not null
    )
    '''
    cur.execute(sql1)
    conn.commit()
    print('测试表已创建')
    # for c_name, c_link in chapter.items():
    #     c_name = chapter.keys()
    #     c_link = chapter.values()
    #     # for i in range(len(c_name)):
    #     #     c_name[i] =
    c_name = chapter.keys()
    c_link = chapter.values()
    print(len(c_name))
    for i in range(len(c_name)):
        chapter_name = '"'+list(c_name)[i]+'"'
        chapter_link = '"'+list(c_link)[i]+'"'
        sql2 = '''
        insert into test_chapter(chapter_name,chapter_link)
        values ({c_name},{c_link})
        '''.format(c_name=chapter_name,c_link=chapter_link)
        cur.execute(sql2)
        conn.commit()
    cur.close()
    conn.close()
    print('章节信息已添加')

def gettext():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    cur = conn.cursor()
    #1显示全部章节名
    sql1 = '''
    select chapter_name from test_chapter
    '''
    cur.execute(sql1)
    conn.commit()
    chapter_name = cur.fetchall()
    for i in chapter_name:
        print(i[0])
    #2获取章节名从而找到章节连接
    input_message = input('请输入章节名或章节数')
    if input_message.isdigit():
        sql2 = '''
        select chapter_link from test_chapter where id={}
        '''.format(input_message)
        cur.execute(sql2)
        conn.commit()
        chapter_link = cur.fetchall()
        # print(chapter_link[0][0])
    else:
        sql3 = '''
        select chapter_link from test_chapter where chapter_name={}
        '''.format(input_message)
        cur.execute(sql3)
        conn.commit()
        chapter_link = cur.fetchall()
        # print(chapter_link[0][0])
    #3获取对应章节的正文内容（视情况处理分页）
    html = ''
    html = askurl(chapter_link[0][0])
    data = parsel.Selector(html)
    text_message = data.xpath('//div[@id="content"]/text()').extract()
    # print(type(text_message),text_message)
    text_message2=''.join(text_message)
    # print(text_message2)
    text_message3 =unicodedata.normalize('NFKC',text_message2)
    print(text_message3)

if __name__ == '__main__':
    main()
