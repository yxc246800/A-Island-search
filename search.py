#-*- coding: utf-8 -*-
import urllib.request as ur
import urllib.parse as up
import re
import sys
import io

#改变标准输入输出的默认编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')

class Spider():

    _base_url    = 'https://tnmb.org/'

    _header      = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/35.0.1916.114 Safari/537.36',
                    'Cookie': 'AspxAutoDetectCookieSupport=1'}

    _blockSets   = ['综合', '技术', '二次创作', '动画漫画', '游戏', '欢乐恶搞', '小说',
                    '数码音乐', '射影', '都市怪谈', '支援1', '基佬', '姐妹2', '日记', '美食',
                    '喵板', '社畜', '车万养老院', '买买买']

    #0  按po主内容+回复内容搜索
    #1  按po主内容搜索
    #2  按串内回复搜索
    _searchWays         = ['0', '1', '2']


    _searchWay          = ''
    _searchBlock        = ''
    _keyword            = ''
    _searchThreadID     = ''
    _INTERVAL           = 1
    _MAX_TRY_NUM        = 5
    _PAGE_NUM     = 1
    _THREAD_PAGE_NUM    = 1
    _RESULT_NUM         = 0
    _TIME_OUT           = 50
    _BATCH_SIZE         = 25


    #初始化
    def __init__(self):
        print('initing... ... ...')
        self.init(5, 50)

    def init(self, max_tryNum, timeOut):

        self._MAX_TRY_NUM = max_tryNum;
        self._TIME_OUT = timeOut;

        self._keyword         = input("请输入搜索关键词：")

        self._searchWay       = input("请输入搜索模式："
                                      "0  按po主内容+回复内容搜索"
                                      "1  按po主内容搜索"
                                      "2  按串内回复搜索")
        while(self._searchWay not in self._searchWays):
            self._searchWay   = input("请重新输入搜索模式，确认其是0,1,2之中的一个（"
                                      "0  按po主内容+回复内容搜索"
                                      "1  按po主内容搜索"
                                      "2  按串内回复搜索")
            print(self._searchWay)

        if(self._searchWay == '2'):
            self._searchThreadID = input("请输入搜索串号：" )
        if(self._searchWay == '1'):
            self._searchBlock     = input("请输入搜索板块：")
            while(self._searchBlock not in self._blockSets):
                self._searchBlock = input("请重新输入查询板块名称，确认其没有输错：")
                print(self._searchBlock)


        self._BATCH_SIZE      = input("请输入每次搜索页数：")
        while(not(self._BATCH_SIZE.isdigit()) or (int(self._BATCH_SIZE) <= 0)):
            self._BATCH_SIZE  = input("请重新输入，并确保其是大于0的数字：")
            print(self._BATCH_SIZE)
        self._BATCH_SIZE = int(self._BATCH_SIZE)


        #板块名称预编码
        self._searchBlock = up.quote(self._searchBlock, encoding='utf-8')

    #获得当页面总页数
    def getPageNum(self, pattern_pageNum=None):
        url                 = ''
        pattern_pageNum     = None
        if self._searchWay == '1':
            url             = self._base_url + 'f/' + str(self._searchBlock) + '?page=' + str(1)
        if self._searchWay == '2':
            url             = self._base_url + 't/' + self._searchThreadID + '?page=' + str(1)
        if(not pattern_pageNum):
            pattern_pageNum = re.compile(r'(?<="uk-pagination uk-pagination-left h-pagination">).*?下一页.*?page=(.*?)">(?=末页)', re.DOTALL)

        data                = self.getData(url)
        match = []
        if data  != '':
            try:
                match = pattern_pageNum.findall(data)
            except Exception as error:
                print(error, 123)
            if match:
                print(match[0])
                return match[0]
            else:
                print(match[0], flush=True)
                print('no match', flush=True)
                pattern_pageNum = re.compile(r'(?<="uk-pagination uk-pagination-left h-pagination">).*<a href=".*?">(.*?)</a>.*?(?=下一页)', re.DOTALL)
                self.getPageNum(pattern_pageNum)


    #获取当前页面数据
    def getData(self, url):
            request  = ur.Request(url=url, data=None, headers=self._header)
            data     = ''
            try:
                html = ur.urlopen(request, timeout=self._TIME_OUT)
                data = html.read()
            except Exception as err:
                print(err, 456)

            #解码
            try:
                data     = str(data, encoding='utf-8')
            except Exception as error:
                print(error, 345)
            return data

    #正则解析数据
    def dataHandle(self, data, key_word):

        pattern_word        = ''
        if self._searchWay == '1':
            pattern_word    = "h-threads-item-main"
        if self._searchWay == '2':
            pattern_word    = "h-threads-item-reply-main"
        if data    != '':
            #第一个：日期
            #第二个：串号
            #第三个：串内容
            pattern = re.compile(r'' + pattern_word + r'(?<=).*?"h-threads-info-createdat">(.*?)(?=</span>)'
                                 r'.*?"h-threads-info-id">+(.*?)(?=</a>)'
                                 r'.*?"h-threads-content">(.*?)(?=</div>)', flags=re.DOTALL)

            match   = pattern.findall(data)
            if match:
                for i in match:
                    b     = i[2].find(key_word)
                    if b != -1:
                        self._RESULT_NUM += 1
                        print('\033[0;32;40m' + i[0].replace(' ', '').replace('<br/>', '') + ' \033[0m', flush=True)
                        print('\033[4;33;40m' + i[1].replace(' ', '').replace('<br/>', '') + ' \033[0m', flush=True)
                        print('\033[1;31;40m' + i[2].lstrip('\r\n').replace(' ', '').replace('<br/>', '') + ' \033[0m', flush=True)

    #搜索
    def search(self):

        url = ''
        try:
            self._PAGE_NUM = int(self.getPageNum())
        except Exception as err:
            print(err, 234)

        for i in range(self._PAGE_NUM+1)[1:]:
            print(i, flush=True)
            if self._searchWay == '1':
                url = self._base_url + 'f/' + str(self._searchBlock) + '?page=' + str(i)
            if self._searchWay == '2':
                url = self._base_url + 't/' + self._searchThreadID + '?page=' + str(i)
            data = self.getData(url)
            self.dataHandle(data, self._keyword)
            if(i % self._BATCH_SIZE == 0):
                input("list " + str(self._BATCH_SIZE) +" pages items "
                        "press anykey to continue... ... ...")


def main():

        spider = Spider()
        spider.search()
        print(spider._RESULT_NUM)

if __name__ == '__main__':
    main()
