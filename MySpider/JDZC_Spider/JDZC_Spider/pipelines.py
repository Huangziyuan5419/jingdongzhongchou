# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import scrapy
import pymongo
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings
from JDZC_Spider.items import JdzcSpiderItem,ImgItem


class JdzcSpiderPipeline(object):
    '''
        对众筹的商品信息进行本地文件保存
    '''
    def __init__(self):
        self.file = open('info.txt', 'w', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if isinstance(item, JdzcSpiderItem):
            line = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.file.write(line)
        return item
#
class ZCImagePipeline(ImagesPipeline):
    '''
        对图片处理的方法，该方法自动实现了异步下载和多线程的处理
    '''
    # 可在settings自己定义存储图片路径
    # IMAGES_STORE = get_project_settings().get('IMAGES_STORE')

    def get_media_requests(self, item, info):
        # 判断item是否为图片item，获取item的信息
        if isinstance(item, ImgItem):
            img_url = item['image_urls']
            print(img_url)
            title = item['title']
            yield scrapy.Request(img_url, meta={'title': title})

    # def item_completed(self, results, item, info):
    #     if isinstance(item, ImgItem):
    #         image_paths = [x['path'] for ok, x in results if ok]
    #         if not image_paths:
    #             raise DropItem("Item contains no images")
    #         return item

        # 修改文件的命名和路径
    def file_path(self, request, response=None, info=None):
        title = request.meta['title']
        filename = './{}.jpg'.format(title)
        return filename

class MongoPipeline(object):
    '''
        将数据保存到 Mongdb 数据库中
    '''
    def __init__(self, host, port, dbname):
        self.host = host
        self.port = port
        self.dbname = dbname

    @classmethod
    def from_crawler(cls, crawler):
        # 获取settings里面的内容
        return cls(
            host = crawler.settings.get('MONGODB_SERVER'),
            port = crawler.settings.get('MONGODB_PORT'),
            dbname = crawler.settings.get('MONGO_DB'),
        )

    def open_spider(self, spider):
        # 连接数据库
        self.client = pymongo.MongoClient(host=self.host, port=self.port)
        self.db = self.client[self.dbname]

    def process_item(self, item, spider):
        if isinstance(item, JdzcSpiderItem):
            # 将item的名字当做表名写入数据
            name = item.__class__.__name__
            self.db[name].insert(dict(item))
            return item

    def close_spider(self, spider):
        self.client.close()