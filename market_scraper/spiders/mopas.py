import traceback
import scrapy
from ..items import MarketItem
from datetime import date


class MopasSpider(scrapy.Spider):
    name = "mopas"
    home_url = "https://www.mopas.com.tr"
    current_date = date.today()
    custom_settings = {
        "FEEDS": {
            f"{name}_{current_date}.csv": {
                "format": "csv",
                "encoding": "utf8",
                "store_empty": False,
                "fields": None,
                "indent": 4,
                "item_export_kwargs": {
                    "export_empty_fields": True,
                }
            }
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.home_url
        )

    def parse(self, response):
        try:
            main_categories = response.css("ul.hidden-sm.col-sm-2.col-md-2.sidebar.nav.nav-sidebar.nav-fixed > li")[2:-1]

            for main_category in main_categories:
                main_category_name = main_category.css(".container-fluid h3 a::text").get()
                sub_categories = main_category.css(".container-fluid ul li a")

                for sub_category in sub_categories:
                    sub_category_name = sub_category.css("::text").get()
                    sub_category_link = self.home_url + sub_category.css("::attr(href)").get()

                    yield scrapy.Request(
                        url=sub_category_link,
                        callback=self.parse_lowest_categories,
                        meta={
                            "categories": {
                                "main_category": main_category_name,
                                "sub_category": sub_category_name
                            }
                        }
                    )
        except:
            traceback.print_exc()

    def parse_lowest_categories(self, response):
        try:
            lowest_categories = response.css("#category li")

            if len(response.css("#category li")) != 0:
                for lowest_category in lowest_categories:
                    lowest_category_name = lowest_category.css("a span::text")[0].get()
                    lowest_category_link = self.home_url + lowest_category.css("a::attr(href)").get()

                    yield scrapy.Request(
                        url=lowest_category_link,
                        callback=self.parse_products,
                        meta={
                            "categories": dict(response.meta["categories"], lowest_category=lowest_category_name)
                        }
                    )
            else:
                response.meta["categories"] = dict(response.meta["categories"], lowest_category=None)
                product_cards = response.css(".card")

                for product_card in product_cards:
                    yield self.get_market_item(product_card, response)

                next_page = self.get_next_page(response)

                if next_page is not None:
                    yield next_page
        except:
            traceback.print_exc()

    def parse_products(self, response):
        try:
            product_cards = response.css(".card")

            for product_card in product_cards:
                yield self.get_market_item(product_card, response)

            next_page = self.get_next_page(response)

            if next_page is not None:
                yield next_page
        except:
            traceback.print_exc()

    def get_market_item(self, product_card, response):
        try:
            product_name = product_card.css("a.product-title::text").get()
            product_link = self.home_url + product_card.css("a.product-title::attr(href)").get()
            product_price = float(product_card.css(".sale-price::text").get()
                                    .replace('₺', '').replace('.', '').replace(',', '.'))
            product_price_high = product_card.css(".old-price::text").get()
            product_price_high = float(product_price_high
                                        .replace('₺', '').replace('.', '')
                                        .replace(',', '.')) if bool(product_price_high) else None
            is_in_stock = bool(product_card.css(".btn.btn-primary.btn-block.js-enable-btn.add-to-basket.addToBasket"
                                                ".gtmProductClick").get())

            return MarketItem(
                main_category=response.meta["categories"]["main_category"],
                sub_category=response.meta["categories"]["sub_category"],
                lowest_category=response.meta["categories"]["lowest_category"],
                name=product_name,
                price=product_price,
                high_price=product_price_high,
                in_stock=is_in_stock,
                product_link=product_link,
                page_link=response.url,
                date=self.current_date
            )
        except:
            traceback.print_exc()

    def get_next_page(self, response):
        next_page_href = response.css(".pagination-next a::attr(href)").get()

        if bool(next_page_href):
            return scrapy.Request(
                url=self.home_url + next_page_href,
                callback=self.parse_products,
                meta={
                    "categories": response.meta["categories"]
                }
            )
        else:
            return None
