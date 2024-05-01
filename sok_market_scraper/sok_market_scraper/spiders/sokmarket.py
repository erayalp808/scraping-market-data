import scrapy


class SokmarketSpider(scrapy.Spider):
    name = "sokmarket"
    allowed_domains = ["sokmarket.com.tr"]
    start_urls = ["https://sokmarket.com.tr"]

    def parse(self, response):
        pass
