# coding=utf-8
# 2018.04.20 T00ls.net
# __author__: ihoneysec
import requests
import logging
from binascii import b2a_hex
from queue import Queue
from threading import Thread
from argparse import ArgumentParser
from copy import deepcopy

logging.basicConfig(level=logging.WARNING, format="%(message)s")


class BakScan(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
        }
        self.timeout = 5  # 3秒测试有漏报

    def _auth(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, timeout=self.timeout, allow_redirects=False, stream=True, verify=False)
            # 验证压缩包文件头10个字节，rar固定头16进制为:526172211a0700cf9073  zip为:504b0304140000000800
            content = b2a_hex(r.raw.read(10)).decode()
            if r.status_code == 200:
                rarsize = int(r.headers.get('Content-Length')) // 1024 // 1024
                if content.startswith('526172') or content.startswith('504b03'):
                    logging.warning('[*] {}  size:{}M'.format(url, rarsize))
                    with open('success.txt', 'a') as f:
                        try:
                            f.write(str(url) + '\n')
                        except:
                            pass
            else:  # 如果你只想看扫描成功的备份地址就注释这行和下一行
                logging.warning('[ ] {}'.format(url))
        except Exception as e:
            pass

    def run(self):
        while not self.queue.empty():
            url = self.queue.get()
            try:
                self._auth(url)
            except:
                continue


def dispatcher(url_file=None, url=None, max_thread=1, dic=None):
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

    with open('success.txt', 'w'):
        pass

    q = Queue()

    for u in urllist:
        # 假设url为www.test.gov.cn，自动根据域名生成一些备份文件名，如下：
        # www.test.gov.cn.rar www.test.gov.cn.zip
        # wwwtestgovcn.rar wwwtestgovcn.zip
        # testgovcn.rar testgovcn.zip
        # test.gov.cn.rar test.gov.cn.zip
        # www.rar www.zip
        www1 = u.split('.')
        wwwlen = len(www1)
        wwwhost = ''
        for i in range(1, wwwlen):
            wwwhost += www1[i]

        current_info_dic = deepcopy(dic)  # 深拷贝
        current_info_dic.extend([u + '.rar', u + '.zip'])
        current_info_dic.extend([u.replace('.', '') + '.rar', u.replace('.', '') + '.zip'])
        current_info_dic.extend([wwwhost + '.rar', wwwhost + '.zip'])
        current_info_dic.extend([u.split('.', 1)[-1] + '.rar', u.split('.', 1)[-1] + '.zip'])
        # print(current_info_dic)
        """ 最终每个url对应可以扫描的字典部分如下
        ['web.rar', 'web.zip', 'backup.rar', 'www.rar', 'bak.rar', 'wwwroot.zip', 'bak.zip', 'www.zip', 'wwwroot.rar', 'backup.zip', 'www.test.gov.cn.rar', 'www.test.gov.cn.zip', 'wwwtestgovcn.rar', 'wwwtestgovcn.zip', 'testgovcn.rar', 'testgovcn.zip', 'test.gov.cn.rar', 'test.gov.cn.zip']
        ['web.rar', 'web.zip', 'backup.rar', 'www.rar', 'bak.rar', 'wwwroot.zip', 'bak.zip', 'www.zip', 'wwwroot.rar', 'backup.zip', 'www.baidu.com.rar', 'www.baidu.com.zip', 'wwwbaiducom.rar', 'wwwbaiducom.zip', 'baiducom.rar', 'baiducom.zip', 'baidu.com.rar', 'baidu.com.zip']
        """

        for info in current_info_dic:
            if u.startswith('http://') or u.startswith('https://'):
                url = str(u) + '/' + str(info)
            else:
                url = 'http://' + str(u) + '/' + str(info)
            q.put(url)

    # print(q.__dict__['queue'])  # 注释掉或删掉这行，如果url批量太多，会满屏幕打印队列中待扫描的地址
    print('队列大小：' + str(q.qsize()))
    threadl = [BakScan(q) for _ in range(max_thread)]
    for t in threadl:
        t.start()

    for t in threadl:
        t.join()


if __name__ == '__main__':
    parser = ArgumentParser(add_help=True, description='Information disclosure scanning tools..')
    parser.add_argument('-f', dest="url_file", help="Set ip file")
    parser.add_argument('-t', dest="max_threads", nargs='?', type=int, default=1, help="Set max threads")
    parser.add_argument('-u', '--url', dest='url', nargs='?', type=str, help="Example: www.xxx.top")

    """
    参数：
        -f 批量时指定存放url的文件
        -t 指定线程
        -u 单个url扫描时指定url
    使用:
        批量url扫描    python3.5 ihoneyBakFileScan.py -t 100 -f url.txt
        单个url扫描    python3.5 ihoneyBakFileScan.py -u www.ihoneysec.top
    """

    args = parser.parse_args()
    # 如果想使用这个脚本的默认扫描字典，请取消注释下一行注释
    info_dic = ['bak.rar', 'bak.zip', 'backup.rar', 'backup.zip', 'www.zip', 'www.rar', 'web.rar', 'web.zip', 'wwwroot.rar', 'wwwroot.zip', ]
    # 如果想从文件中自定义字典请取消下一行注释并注释上一行
    # info_dic = list(set([i.replace("\n", "") for i in open("dic.txt", "r").readlines()]))

    try:
        if args.url:
            dispatcher(url=args.url, max_thread=args.max_threads, dic=info_dic)
        elif args.url_file:
            dispatcher(url_file=args.url_file, max_thread=args.max_threads, dic=info_dic)
        else:
            print("Domain name? urlfile?")
    except Exception as e:
        pass
