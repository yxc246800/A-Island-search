#-*- coding: utf-8 -*-
import urllib.request as ur
import urllib.parse as up
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8') #改变标准输出的默认编码
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

class Spider():

    _base_url = 'https://tnmb.org/'
    _header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
        AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/35.0.1916.114 Safari/537.36',
        'Cookie': 'AspxAutoDetectCookieSupport=1'
        }
    _blockSets = ['综合', '技术', '二次创作', '动画漫画', '游戏', '欢乐恶搞', '小说',
                  '数码音乐', '射影', '都市怪谈', '支援1', '基佬', '姐妹2', '日记', '美食',
                  '喵板', '社畜', '车万养老院', '买买买']
    _searchBlock = ''
    #0  按po主内容+回复内容搜索
    #1  按po主内容搜索
    #2  按串内回复搜索
    _searchWays = ['0', '1', '2']
    _searchWay = ''

    _interval = 1
    _keyword = ''
    _max_tryNum = 5
    _block_pageNum = 1
    _thread_pageNum = 1
    _result_num = 0

    def __init__(self):
        print('init')
        self.init(5, 50, 50)

    def init(self, max_tryNum, timeOut, batchSize):
        print(self._blockSets[0])
        self._keyword = input("请输入搜索关键词：")

        self._searchBlock = input("请输入搜索板块：")
        while (self._searchBlock not in self._blockSets):
            self._searchBlock = input("请重新输入查询板块名称，确认其没有输错：")
            print(self._searchBlock)

        self._searchWay = input("请输入搜索模式："
                                "0  按po主内容+回复内容搜索"
                                "1  按po主内容搜索"
                                "2  按串内回复搜索")
        while(self._searchWay not in self._searchWays):
            self._searchWay = input("请重新输入搜索模式，确认其是0,1,2之中的一个（"
                                     "0  按po主内容+回复内容搜索"
                                     "1  按po主内容搜索"
                                     "2  按串内回复搜索")
            print(self._searchWay)


        #板块名称预编码
        #for i in range(len(self._blockSets)):
        self._searchBlock = up.quote(self._searchBlock, encoding='utf-8')

    def getPageNum(self):
        pattern_pageNum = re.compile(r'(?<="uk-pagination uk-pagination-left h-pagination">).*?下一页.*?page=(.*?)">(?=末页)', re.DOTALL)
        data = self.getData(1)

        if data != '':
            match = pattern_pageNum.findall(data)
            if match:
                return match[0]

    def getData(self, pageNum):
            #print((self._blockSets[0]))
            url = self._base_url + 'f/' + str(self._searchBlock) + '?page=' + str(pageNum)
            #print(url)
            request = ur.Request(url=url, data=None, headers=self._header)
            data = ''
            try:
                html = ur.urlopen(request, timeout=12)
                data = html.read()
            except Exception as err:
                print(err)

            #解码
            #print(type(data))
            data = str(data, encoding='utf-8')
            #print(data)
            return data

    def dataHandle(self, data, key_word):
        #正则解析数据
            if data != '':
                print("data exists")
                #pattern_title = re.compile(r'(?<="h-threads-item-main").*?"h-threads-content">(.*?)(?=</div>)', flags=re.DOTALL|re.MULTILINE)
                #pattern_uid = re.compile(r'(?<="h-threads-item-main").*?"h-threads-info-id">+(.*?)(    ?=</a>)', flags=re.DOTALL)
                #pattern_date = re.compile(r'(?<="h-threads-item-main").*?"h-threads-info-createdat">(.*?)(?=</span>)', flags=re.DOTALL)

                pattern = re.compile(r'(?<="h-threads-item-main").*?"h-threads-info-createdat">(.*?)(?=</span>)'
                                     r'.*?"h-threads-info-id">+(.*?)(?=</a>)'
                                     r'.*?"h-threads-content">(.*?)(?=</div>)', flags=re.DOTALL)

                match = pattern.findall(data)
                #match_title = pattern_title.findall(data)
                #match_uid = pattern_uid.findall(data)
                #match_date = pattern_date.findall(data)

                #length = len(match_title)
                if match:
                    for i in match:
                        b = i[2].find(key_word)
                        if b != -1:
                            self._result_num += 1
                            print('\033[0;32;40m' + i[0].replace(' ', '').replace('<br/>', '') + ' \033[0m', flush=True)
                            print('\033[4;33;40m' + i[1].replace(' ', '').replace('<br/>', '') + ' \033[0m', flush=True)
                            print('\033[1;31;40m' + i[2].lstrip('\r\n').replace(' ', '').replace('<br/>', '') + ' \033[0m', flush=True)
                        #print( (match_date[i]).replace(' ', '').replace('<br/>', ''))
                        #print( (match_uid[i]).replace(' ', '').replace('<br/>', ''))
                        #print( (match_title[i]).lstrip('\r\n').replace(' ', '').replace('<br/>', ''))

    def search(self):
        self._block_pageNum = int(self.getPageNum())


        for i in range(self._block_pageNum+1)[1:]:
            print(i, flush=True)
            data = self.getData(i)
            self.dataHandle(data, self._keyword)

def main():

        spider = Spider()
        spider.search()
        print(spider._result_num)

if __name__ == '__main__':
    main()
