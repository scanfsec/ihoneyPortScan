# coding=utf-8
import requests
import logging
from queue import Queue
from threading import Thread
from argparse import ArgumentParser

logging.basicConfig(level=logging.WARNING, format="%(message)s")

"""
可能存在信息泄露的文件：
/.git/config 未完成检测代码
/.svn/entries 未完成检测代码
/WEB-INF/web.xml  已完成

1.重写线程类
全局请求超时时间
auth函数（主要验证功能块）
run函数调用auth函数

2.分发函数
创建队列
实例化线程类并启动线程

3.主函数内容
3.1 扫描文件字典：
.git/config   关键词：
.svn/entries  关键词：
WEB-INF/web.xml 关键词：</web-app>
3.2 定义线程数
3.3 从文件去除url组合加上字典,文件每行不需要添加http(加了也会给你去掉)
"""


class PortScan(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
            'Connection': 'close'
        }
        self.timeout = 5
        self.webinfkey = "</web-app>"

    def _auth(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, timeout=self.timeout, allow_redirects=False)
            content = r.text

            if self.webinfkey in content and r.status_code == 200:
                logging.warning("[*] {}".format(url))
                with open('info.txt', 'a') as f:
                    try:
                        f.write(str(url) + '\n')
                    except:
                        pass
        except Exception:
            pass

    def run(self):
        while not self.queue.empty():
            url = self.queue.get()
            try:
                self._auth(url)
            except:
                continue


def dispatcher(url_file=None, url=None, max_thread=100, info_dic=None):
    urllist = []
    if url_file is not None and url is None:
        with open(str(url_file)) as f:
            while True:
                line = str(f.readline()).strip()
                if line:
                    urllist.append(line)
                else:
                    break
    elif url is not None and url_file is None:
        urllist.append(url)
    else:
        pass

    with open('info.txt', 'w'):
        pass

    q = Queue()
    for url in urllist:
        url = url.strip('http://').strip('https://').strip('/')
        for info in info_dic:
            url = 'http://' + str(url) + '/' + str(info)  # url:www.xx.com info:WEB-INF/web.xml
            q.put(url)

    # print(q.__dict__['queue'])
    qsize = q.qsize()
    print('队列大小：' + str(qsize))

    threadl = [PortScan(q) for _ in range(max_thread)]
    for t in threadl:
        t.start()

    for t in threadl:
        t.join()


if __name__ == '__main__':
    parser = ArgumentParser(add_help=True, description='Information disclosure scanning tools..')
    parser.add_argument('-f', dest="url_file", help="Set ip file")
    parser.add_argument('-t', dest="max_threads", nargs='?', type=int, default=1, help="Set max threads")
    parser.add_argument('-u', '--url', dest='url', nargs='?', type=str, help="Example: www.xxx.top")

    args = parser.parse_args()
    info_dic = ['WEB-INF/web.xml']

    try:
        if args.url:
            dispatcher(url=args.url, max_thread=args.max_threads, info_dic=info_dic)
        elif args.url_file:
            dispatcher(url_file=args.url_file, max_thread=args.max_threads, info_dic=info_dic)
        else:
            print("Domain name? urlfile?")
    except Exception as e:
        print(e)