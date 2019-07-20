# -*- coding: utf-8 -*-
import scrapy
from JDZC_Spider.items import JdzcSpiderItem,ImgItem


class JdzcSpider(scrapy.Spider):
    name = 'jdzc'
    allowed_domains = ['z.jd.com']
    start_urls = ['https://z.jd.com/bigger/search.html']

    def start_requests(self):
        # 京东众筹为post请求，需要添加form_data
        url = 'https://z.jd.com/bigger/search.html'
        for page in range(1,101):
            form_data = {
                'page': str(page),
            }
            print(form_data)
            request = scrapy.FormRequest(url=url, formdata=form_data, callback=self.parse)
            yield request

    def parse(self, response):
        # 获取相应的一些资料
        lis = response.xpath('//div[@class="l-result"]/ul/li')
        for li in lis:
            title = li.xpath('.//div[contains(@class, "i-tits")]/a/h4/text()').get()
            arrived = ''.join(
                li.xpath('.//div[contains(@class, "p-outter")]/div[@class="p-items"]/ul/li[@class="fore1"]/p/text()').getall())
            raised = ''.join(
                li.xpath('.//div[contains(@class, "p-outter")]/div[@class="p-items"]/ul/li[@class="fore2"]/p/text()').getall())
            residue_days = ''.join(
                li.xpath('.//div[contains(@class, "p-outter")]/div[@class="p-items"]/ul/li[@class="fore3"]/p/text()').getall())
            # print(title, arrived, raised, residue_days)
            # 众筹商品的详细链接
            link = 'http://z.jd.com' + li.xpath('.//a[@class="link-pic"]/@href').get()
            # print(link)
            # 商品的图片链接
            img_url = 'https:' + li.xpath('.//a[@class="link-pic"]/img/@src').get()
            # 将详情链接发送给下载器对详情链接爬取
            yield scrapy.Request(url=link, callback=self.parse_goods, meta={'info': (title, arrived, raised, residue_days, img_url)})

    def parse_goods(self, response):
        # 处理详情链接里面的一些资料
        title, arrived, raised, residue_days, img_url = response.meta.get('info')
        # print(title, arrived, raised, residue_days)
        promotos_name = response.xpath('//div[@class="wrap"]//div[@class="promoters-name"]//span[@class="fl"]/text()').get().strip()
        # print(promotos_name)
        contect = ''.join(response.xpath('//div[@class="box-content"]/ul[@class="contact-box"]/li/div/text()').getall())
        # for li in ls:
        #     contect = ''.join(li.xpath('.//div/text()').getall())
        #     print(type(contect))
        # print(contect)

        # 定义两item  一个是普通item  另一个是图片的item
        item = JdzcSpiderItem()
        item['promotos_name'] = promotos_name
        item['title'] = title
        item['arrived'] = arrived
        item['raised'] = raised
        item['residue_days'] = residue_days
        item['contect'] = contect
        item['img_url'] = img_url
        yield item
        img_item = ImgItem()
        img_item['image_urls'] = img_url
        img_item['title'] = title
        yield img_item




