# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MarketItem(scrapy.Item):
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    lowest_category = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    high_price = scrapy.Field()
    in_stock = scrapy.Field()
    product_link = scrapy.Field()
    page_link = scrapy.Field()
    date = scrapy.Field()
