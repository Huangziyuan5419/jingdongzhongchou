import os
import time
import requests
import random
from lxml import etree
from multiprocessing import Queue, Process,Pool


class Proxy():
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }


    def __init__(self, page=5):
        self.page = page
        self.proxy_list = []

        # 自动开启代理抓取
        self.get_proxy_nn()
        # 检测代理
        self.verify_proxy()


    def get_proxy_nn(self):
        '''
        抓取随机的几页代理
        获取相应的代理
        :return: 
        '''
        page_start = random.randint(1, 5)
        page_stop = page_start + self.page
        while page_start < page_stop:
            url = 'https://www.xicidaili.com/nn/{}'.format(page_start)
            # print(url)
            if requests.get(url, headers=self.headers).status_code == 200:
                time.sleep(2)
                response = requests.get(url, headers=self.headers).text
                self.parse(response)
                page_start += 1
            else:
                print('可能需要换代理')
                exit()

    def parse(self,response):
        '''
        解析
        :param response: 
        :return: 将所有的代理放入列表
        '''

        # exit()
        html = etree.HTML(response)
        tr_list = html.xpath('//table[@id="ip_list"]//tr[@class="odd"]')
        for tr in tr_list:
            protocol = tr.xpath('.//td[6]/text()')[0]
            ip = tr.xpath('.//td[2]/text()')[0]
            port = tr.xpath('.//td[3]/text()')[0]
            proxy = protocol.lower() + "://" + ip + ":" +port
            self.proxy_list.append(proxy)

    def verify_proxy(self):
        # 没验证的代理
        old_queue = Queue()
        # 验证后的代理
        new_queue = Queue()

        works = []
        # pool = Pool(15)
        # for i in range(15):
        #     pool.apply_async(self.verify_one_proxy, args=(old_queue, new_queue))
        #
        # pool.close()
        # pool.join()

        for _ in range(15):
            works.append(Process(target=self.verify_one_proxy, args=(old_queue, new_queue)))
        for work in works:
            work.start()
        for proxy in self.proxy_list:
            old_queue.put(proxy)
        for _ in works:
            old_queue.put(0)
        for work in works:
            work.join()
        self.proxy_list = []
        while True:
            try:
                self.proxy_list.append(new_queue.get(timeout=1))
            except:
                break
        self.useful_proxies_file()
        print('verify_proxies done!')


    def verify_one_proxy(self, old_queue, new_queue):
        while True:
            url = 'http://www.baidu.com'
            proxy = old_queue.get()
            # try:
            #     proxy = old_queue.get(timeout=2)
            # except:
            #     pass
            if proxy == 0:
                break
            protocol = "https" if "https" in proxy else "http"
            proxies = {protocol: proxy}
            try:
                if requests.get(url, proxies=proxies, headers=self.headers, timeout=1).status_code == 200:
                    print("success %s" % proxy)
                    new_queue.put(proxy)
            except:
                print('fail %s' % proxy)

    # 把之前代理文件删掉，重新写入可用的代理
    def useful_proxies_file(self):
        while True:
            if os.path.exists('proxies.txt'):
                os.remove('proxies.txt')
            else:
                with open('proxies.txt', 'a') as f:
                    for proxy in self.proxy_list:
                        f.write(proxy + '\n')
                break


if __name__ == '__main__':
    Proxy()