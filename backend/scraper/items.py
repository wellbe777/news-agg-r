import scrapy

class ArticleItem(scrapy.Item):
    source_name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    image_url = scrapy.Field()
    published_at = scrapy.Field()
    categories = scrapy.Field()
