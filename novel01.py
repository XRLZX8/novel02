#-*- coding = utf-8 -*-
"""
@author: XRL
@software: PyCharm
@file: novel01.py
@time: 2020/8/1 20:59
"""

'''
地址：https://www.biqubao.com/
'''

from bs4 import BeautifulSoup
import urllib.response,urllib.request,urllib.error
import parsel
import re
import pymysql
import unicodedata


baseurl ='https://www.biqubao.com'

find_book_name = re.compile(r'<span>(.*)</span>')
find_book_link = re.compile(r'href="(.*)" title=')
find_chapter = re.compile(r'<a href="(.*)">(.*)</a>')

#-----------
host = 'localhost'
port = 3306
user = 'XRL'
password = 'GTX1070xrl@123'
database = 'novel01'
#-----------

def main(url):
    chapter_dict = {}#小说章节列表:章节链接
    datalist = []#小说正文，按章节分
    chapter_dict = getchapter(url)
    savechapter(chapter_dict)
    chapter_name,text_message=gettext()
    savetest(chapter_name,text_message)
    show_text(text_message)

def getchapter(url):
    html1 = ''
    html1 = askurl(url)
    # print(html1)
    #使用保存到本地的网页制作
    # with open('html/小说搜索——结果.html',encoding='utf-8')as h1:
    #     html1 = h1.read()
    data = parsel.Selector(html1)
    message1 = data.xpath('//a[@cpos="title"]').extract()
    book_name = re.findall(find_book_name,str(message1))#获取网页中书名
    book_link = re.findall(find_book_link,str(message1))#获取书籍页面链接尾部
    book_url = book_link[0]
    # print(book_link)
    # print(book_url)
    novel_url = baseurl+book_url
    html2 = ''
    html2 = askurl(novel_url)
    #使用保存到本地的网页制作
    # with open('html/黎明之剑最新章节列表_黎明之剑全文阅读 - 笔趣阁.html',encoding='gbk')as h2:
    #     html2 = h2.read()
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
    return chapter

def savechapter(chapter):
    #初始化章节表
    init_table_chapter()

    conn = pymysql.connect(host=host,port=port,user=user,password=password,
                           database=database)
    cur = conn.cursor()
    c_name = chapter.keys()
    c_link = chapter.values()
    print(len(c_name))
    for i in range(len(c_name)):
        chapter_name = '"'+list(c_name)[i]+'"'
        chapter_link = '"'+list(c_link)[i]+'"'
        sql2 = '''
        insert into chapter(chapter_name,chapter_link)
        values ({c_name},{c_link})
        '''.format(c_name=chapter_name,c_link=chapter_link)
        cur.execute(sql2)
        conn.commit()
    cur.close()
    conn.close()
    print('章节信息已添加')

def count_chapter():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    cur = conn.cursor()
    sql = '''
    select count(*) from chapter
    '''
    cur.execute(sql)
    conn.commit()
    num = cur.fetchall()[0][0]
    return num

def gettext():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    cur = conn.cursor()
    #1显示全部章节名
    sql1 = '''
    select chapter_name from chapter
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
        select chapter_link from chapter where id={}
        '''.format(input_message)
        cur.execute(sql2)
        conn.commit()
        chapter_link = cur.fetchall()[0][0]
        # print(chapter_link[0][0])
    else:
        sql3 = '''
        select chapter_link from chapter where chapter_name={}
        '''.format(input_message)
        cur.execute(sql3)
        conn.commit()
        chapter_link = cur.fetchall()[0][0]

        #根据连接获取章节名，用于正文保存
    print(chapter_link)
    link = "'"+chapter_link+"'"
    sql4='''
    select chapter_name from chapter where chapter_link={}
    '''.format(link)
    cur.execute(sql4)
    conn.commit()
    chapter_name_2 = cur.fetchall()[0][0]
    print(chapter_name_2)

    #3获取对应章节的正文内容（视情况处理分页）
    html = ''

    chapter_url = baseurl+chapter_link
    print(chapter_link)
    print(chapter_url)
    html = askurl(chapter_url)
    data = parsel.Selector(html)
    text_message = data.xpath('//div[@id="content"]/text()').extract()
    text_message2=''.join(text_message)
    text_message3 =unicodedata.normalize('NFKC',text_message2)
    cur.close()
    conn.close()
    print(text_message3)
    return chapter_name_2,text_message3

def show_text(text_message):
    print(text_message)


def savetest(chapter_name,text_message):
    #初始化正文表
    init_table_text()
    text_message = "'"+text_message+"'"
    chapter_name = "'"+chapter_name+"'"
    # print(text_message)
    conn = pymysql.connect(host=host,port=port,user=user,password=password,database=database)
    cur = conn.cursor()
    sql1 = '''
    insert into novel_text(chapter_name,novel_text)
    value ({c_name},{n_text})
    '''.format(c_name=chapter_name,n_text=text_message)
    cur.execute(sql1)
    conn.commit()
    cur.close()
    conn.close()

def askurl(url):

    head = {
        "User-Agent": "Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit/537.36(KHTML, likeGecko) Chrome / 78.0.3904.108 Safari / 537.36"
    }
    request = urllib.request.Request(url=url,headers=head)
    html = ''
    new_html = ''
    response = urllib.request.urlopen(request)
    html = response.read()
    if 'charset=gbk'.lower() in str(html):
        new_html = html.decode('gbk')
    elif 'charset=utf-8'.lower() in str(html):
        new_html = html.decode('utf-8')
    else:
        new_html = html.decode('utf-8')
    # print(html)
    # print(new_html)
    return new_html

def init_table_chapter():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    cur = conn.cursor()
    sql1 = '''
    create table if not exists chapter(
    id int not null primary key AUTO_INCREMENT,
    chapter_name varchar(255) not null,
    chapter_link text not null
    )
    '''
    cur.execute(sql1)
    conn.commit()
    cur.close()
    conn.close()

def init_table_text():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    cur = conn.cursor()
    sql1 = '''
    create table if not exists novel_text(
    id int not null primary key AUTO_INCREMENT,
    chapter_name varchar(255) not null,
    novel_text text not null
    )
    '''
    cur.execute(sql1)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    base_search_url = 'https://www.biqubao.com/search.php?q='
    novel_name = urllib.request.quote(input('请输入小说名'))
    full_url = base_search_url + novel_name
    print(full_url)
    try:
        main(full_url)
    except urllib.error.HTTPError as e:
        print('ops')
        print(e.code)
