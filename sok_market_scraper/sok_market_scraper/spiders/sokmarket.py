import random
import scrapy
import pandas as pd
from numpy import nan
from math import ceil
from ..items import SokMarketScraperItem
from datetime import date


class SokmarketSpider(scrapy.Spider):
    name = "sokmarket"
    allowed_domains = ["sokmarket.com.tr"]
    start_urls = ["https://sokmarket.com.tr"]

    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 '
        'Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
        'Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 '
        'Safari/537.36 Edg/87.0.664.75',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 '
        'Safari/537.36 Edge/18.18363',
    ]
    current_date = date.today()
    home_url = "https://www.sokmarket.com.tr/"

    def parse(self, response):
        main_category_tags: scrapy.selector.unified.SelectorList = response.css('.CategoryList_categories__wmXtl')
        main_categories = pd.DataFrame({
            'names': main_category_tags.css('span::text').getall()[2:-1],
            'links': list(
                map(lambda href: self.home_url + href, main_category_tags.css('a::attr(href)').getall()[2:-1]))
        })

        for index, name, link in main_categories.itertuples():
            yield response.follow(link, callback=self.parse_sub_categories, meta={'info': name},
                                  headers={"User-Agent": random.choice(self.user_agent_list)})

    def parse_sub_categories(self, response):
        main_category = response.meta['info']
        sub_category_tags: scrapy.selector.unified.SelectorList = (response
                                                                   .css('.CCollapse-module_cCollapseContent__sR6gM'))
        sub_categories = pd.DataFrame({
            'sub_category': sub_category_tags.css('div a::text').getall(),
            'links': list(map(lambda href: self.home_url + href, sub_category_tags.css('div a::attr(href)').getall()))
        })

        for index, name, link in sub_categories.itertuples():
            yield response.follow(link, callback=self.parse_products, meta={'info': (main_category, name)},
                                  headers={"User-Agent": random.choice(self.user_agent_list)})

    def parse_product_quantity(self, response):
        number_of_pages = ceil(int(response.css('p.PLPDesktopHeader_quantityInfoText__4AiWN::text')
                                   .get().split()[0]) / 20)

        current_page_number = 0
        while current_page_number < number_of_pages:
            current_page_number += 1
            next_page_url = response.url + f'?page={current_page_number}'
            yield response.follow(next_page_url, callback=self.parse_products,
                                  meta={'info': response.meta['info']},
                                  headers={"User-Agent": random.choice(self.user_agent_list)})

    def parse_products(self, response):
        main_category, sub_category = response.meta['info']
        product_names = response.css('.PLPProductListing_PLPCardParent__GC2qb h2::text').getall()
        product_links = list(map(lambda href: self.home_url + href,
                                 response.css('.PLPProductListing_PLPCardParent__GC2qb a::attr(href)').getall()))
        product_price_boxes: scrapy.selector.unified.SelectorList = response.css('.CPriceBox-module_cPriceBox__1OWBR')
        product_prices = []
        product_prices_high = []

        for price_box in product_price_boxes:
            discount_price_tag = price_box.css('.CPriceBox-module_discountedPriceContainer__nsaTN')
            if discount_price_tag:
                product_prices_high.append(discount_price_tag.css('.CPriceBox-module_price__bYk-c span::text')
                                           .get().replace('₺', '').replace('.', '').replace(',', '.'))
                product_prices.append(
                    discount_price_tag.css('span.CPriceBox-module_discountedPrice__15Ffw::text')
                    .get().replace('₺', '').replace('.', '').replace(',', '.'))
            else:
                product_prices_high.append(nan)
                product_prices.append(price_box.css('span.CPriceBox-module_price__bYk-c::text')
                                      .get().replace('₺', '').replace('.', '').replace(',', '.'))

        products = pd.DataFrame({
            'category2': main_category,
            'category1': sub_category,
            'category': sub_category,
            'prod': product_names,
            'price': product_prices,
            'high_price': product_prices_high,
            'prod_link': product_links,
            'pages': response.url,
            'date': self.current_date
        })

        for index, row in products.iterrows():
            product = SokMarketScraperItem(
                category2=row['category2'],
                category1=row['category1'],
                category=row['category'],
                prod=row['prod'],
                price=row['price'],
                high_price=row['high_price'],
                prod_link=row['prod_link'],
                pages=row['pages'],
                date=row['date']
            )

            yield product
