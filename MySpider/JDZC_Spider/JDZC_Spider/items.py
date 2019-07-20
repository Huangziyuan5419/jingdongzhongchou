import scrapy


class JdzcSpiderItem(scrapy.Item):
    promotos_name = scrapy.Field()
    title = scrapy.Field()
    arrived = scrapy.Field()
    raised = scrapy.Field()
    residue_days = scrapy.Field()
    contect = scrapy.Field()
    img_url = scrapy.Field()

class ImgItem(scrapy.Item):
    title = scrapy.Field()
    image_urls = scrapy.Field()