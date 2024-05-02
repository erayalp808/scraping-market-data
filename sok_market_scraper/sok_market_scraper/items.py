# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SokMarketScraperItem(scrapy.Item):
    category2 = scrapy.Field()
    category1 = scrapy.Field()
    category = scrapy.Field()
    prod = scrapy.Field()
    price = scrapy.Field()
    high_price = scrapy.Field()
    prod_link = scrapy.Field()
    pages = scrapy.Field()
    date = scrapy.Field()
