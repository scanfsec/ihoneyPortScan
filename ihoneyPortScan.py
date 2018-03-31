# coding=utf-8
from queue import Queue
from threading import Thread
from telnetlib import Telnet
from base64 import b64decode
from argparse import ArgumentParser
from ipaddress import ip_address


class PortScan(Thread):
    TIMEOUT = 5  # 默认扫描超时时间

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def auth(self, url):
        host = url.split(':')[0]
        port = url.split(':')[-1]

        try:
            tn = Telnet(host=host, port=port, timeout=self.TIMEOUT)
            # 越高,得到的调试输出就越多(sys.stdout)。
            tn.set_debuglevel(3)
            print('[*] ' + url + ' -- ok')

            with open('ok.txt', 'a') as f:
                try:
                    f.write(str(url) + '\n')
                except:
                    pass
        except Exception as e:
            # print('[ ] ' + url + ' -- ' + str(e))
            pass
        finally:
            tn.close()

    def run(self):  # 非空
        while not self.queue.empty():
            url = self.queue.get()
            try:
                self.auth(url)
            except:
                continue


def dispatcher(ip_file=None, ip=None, max_thread=100, portlist=None):
    iplist = []
    if ip_file is not None and ip is None:
        with open(str(ip_file)) as f:
            while True:
                line = str(f.readline()).strip()
                if line:
                    iplist.append(line)
                else:
                    break
    elif ip is not None and ip_file is None:
        iplist.append(ip)
    else:
        pass

    with open('ok.txt', 'w'):
        pass

    q = Queue()
    for ip in iplist:
        for port in portlist:
            url = str(ip) + ':' + str(port)
            q.put(url)

    # print(q.__dict__['queue'])
    print('队列大小：' + str(q.qsize()))

    threadl = [PortScan(q) for _ in range(max_thread)]
    for t in threadl:
        t.start()

    for t in threadl:
        t.join()


if __name__ == '__main__':
    parser = ArgumentParser(add_help=True, description='Port scan tool..')
    parser.add_argument('-f', dest="ip_file", help="Set ip file")
    parser.add_argument('-t', dest="max_threads", nargs='?', type=int, default=1, help="Set max threads")
    parser.add_argument('--ip', dest='ip', nargs='?', type=str, help="Example: 192.168.0.105, www.xxx.top")
    parser.add_argument('--port', dest='port', nargs='?', type=str, help="Example: 80    80-89    80,443,3306,8080")

    args = parser.parse_args()
    logo_code = 'IF8gXyAgICAgICAgICAgICAgICAgICAgICAgICAgICBfX19fICAgICAgICAgICAgXyAgIF9fX18gICAgICAgICAgICAgICAgICAKKF8pIHxfXyAgIF9fXyAgXyBfXyAgIF9fXyBfICAgX3wgIF8gXCBfX18gIF8gX198IHxfLyBfX198ICBfX18gX18gXyBfIF9fICAKfCB8ICdfIFwgLyBfIFx8ICdfIFwgLyBfIFwgfCB8IHwgfF8pIC8gXyBcfCAnX198IF9fXF9fXyBcIC8gX18vIF9gIHwgJ18gXCAKfCB8IHwgfCB8IChfKSB8IHwgfCB8ICBfXy8gfF98IHwgIF9fLyAoXykgfCB8ICB8IHxfIF9fXykgfCAoX3wgKF98IHwgfCB8IHwKfF98X3wgfF98XF9fXy98X3wgfF98XF9fX3xcX18sIHxffCAgIFxfX18vfF98ICAgXF9ffF9fX18vIFxfX19cX18sX3xffCB8X3wKICAgICAgICAgICAgICAgICAgICAgICAgICB8X19fLyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAK'
    print(b64decode(logo_code).decode())
    print("Example：\npython3.5 portScan.py --ip 192.168.0.105 --port 20-3390 -t 100\npython3.5 portScan.py --ip www.xxx.top --port 80,443,3306,3389,8080 \npython3.5 xingyuPortScan1.2.py -f ip.txt -t 100")
    print('-' * 64)

    portlist1 = args.port
    if portlist1:
        if ',' in portlist1:
            portlist = portlist1.split(',')
        elif '-' in portlist1:
            portlist = portlist1.split('-')
            tmpportlist = []
            [tmpportlist.append(i) for i in range(int(portlist[0]), int(portlist[1]) + 1)]
            portlist = tmpportlist
        else:
            portlist = [portlist1]
    else:
        portlist = [21, 22, 23, 53, 80, 111, 139, 161, 389, 443, 445, 512, 513, 514,
                    873, 1025, 1433, 1521, 3128, 3306, 3311, 3312, 3389, 5432, 5900,
                    5984, 6082, 6379, 7001, 7002, 8000, 8080, 8081, 8090, 9000, 9090,
                    8888, 9200, 9300, 10000, 11211, 27017, 27018, 50000, 50030, 50070]
        print('You do not specify a port, will only scan has set the default port')

    if args.ip:
        try:
            # ip_address(args.ip)
            dispatcher(ip=args.ip, max_thread=args.max_threads, portlist=portlist)
        except Exception as e:
            print(e)
    elif args.ip_file:
        dispatcher(ip_file=args.ip_file, max_thread=args.max_threads, portlist=portlist)
    else:
        print("Please specify the IP address or domain name and the port scanning")
