import scrapy
from numpy import nan
from scrapy.crawler import CrawlerProcess

from ..items import MarketItem
from datetime import date
import random


class CarrefourSpider(scrapy.Spider):
    name = "carrefour"
    allowed_domains = ["carrefoursa.com"]
    start_urls = ["https://carrefoursa.com"]

    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 "
        "Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 "
        "Safari/537.36 Edg/87.0.664.75",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 "
        "Safari/537.36 Edge/18.18363",
    ]
    current_date = date.today()

    def parse(self, response):
        categories = response.css("li.main-menu-item")

        for category in categories:
            main_category_name = category.css("a.main-menu-item-link  span:nth-child(2)::text").get().strip()

            sub_categories = category.css("li.main-menu-dropdown-item")

            for sub_category in sub_categories:
                sub_category_name = sub_category.css("a.main-menu-dropdown-item-link::text").get().strip()
                sub_category_url = sub_category.css("a.main-menu-dropdown-item-link::attr(href)").get()

                lowest_categories = sub_category.css("a.main-menu-dropdown-item-sub-link")

                if len(lowest_categories) >= 1:
                    for lowest_category in lowest_categories:
                        lowest_category_name = lowest_category.css("::text").get().strip()
                        lowest_category_url = lowest_category.attrib["href"]
                        info = {
                            "main_category": main_category_name,
                            "sub_category": sub_category_name,
                            "lowest_category": lowest_category_name
                        }

                        yield response.follow(self.start_urls[0][:-1] + lowest_category_url,
                                              callback=self.parse_category_page,
                                              meta={"info": info},
                                              headers={"User-Agent": random.choice(self.user_agent_list)})
                else:
                    info = {
                        "main_category": main_category_name,
                        "sub_category": sub_category_name,
                        "lowest_category": None
                    }

                    yield response.follow(self.start_urls[0][:-1] + sub_category_url,
                                          callback=self.parse_category_page,
                                          meta={"info": info},
                                          headers={"User-Agent": random.choice(self.user_agent_list)})

    def parse_category_page(self, response):
        product_cards = response.css("li.product-listing-item .hover-box")

        for product_card in product_cards:
            is_out_of_stock = bool(product_card.css(".oos-cont").get())

            if is_out_of_stock: continue
            product_name = product_card.css(".item-name::text").get()
            product_price = float(product_card.css("span.item-price").attrib["content"])
            product_price_high = self.parse_price_high(product_card)
            product_link = self.start_urls[0][:-1] + product_card.css("a::attr(href)").get()

            product = MarketItem(
                category2=response.meta["info"]["main_category"],
                category1=response.meta["info"]["sub_category"],
                category=response.meta["info"]["lowest_category"],
                prod=product_name,
                price=product_price,
                high_price=product_price_high,
                prod_link=product_link,
                pages=response.url,
                date=self.current_date
            )

            yield product

        next_page = self.get_next_page(response)

        if next_page is not None:
            yield response.follow(self.start_urls[0][:-1] + next_page,
                                  callback=self.parse_category_page,
                                  meta={"info": response.meta["info"]})

    def parse_price_high(self, product_card):
        whole_part = product_card.css("span.priceLineThrough::text").get()

        if whole_part is not None:
            whole_part = whole_part.strip().removesuffix(',').replace('.', '')
            cents = product_card.css("span.formatted-price::text").get().strip()
            cents = cents.removesuffix('TL').strip()
            price_high = float(whole_part + '.' + cents)

            return price_high
        else:
            return nan

    def get_next_page(self, category_page):
        current_page = category_page.css(".pagination-item.active ::text").get()

        if current_page is not None:
            current_page = int(current_page)
            next_pages = category_page.css(".pagination-item ::attr(href)").getall()
            next_pages = next_pages[current_page - 1:]

            if len(next_pages) > 0:
                return next_pages[0]
            else:
                return None
        else:
            return None
