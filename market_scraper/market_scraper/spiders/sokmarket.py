import scrapy
import pandas as pd
from math import ceil
from ..items import MarketItem
from datetime import date


class SokmarketSpider(scrapy.Spider):
    name = "sokmarket"
    current_date = date.today()
    home_url = "https://www.sokmarket.com.tr/"

    def start_requests(self):
        yield scrapy.Request(url=self.home_url, meta={
            "playwright": True,
            "playwright_include_page": True
        })

    async def parse(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.wait_for_load_state("networkidle")
            content = await page.content()
            await page.close()

            selector = scrapy.Selector(text=content)
            main_category_tags = selector.css(".CategoryList_categories__wmXtl")[0]
            main_categories = pd.DataFrame({
                "names": main_category_tags.css("span::text").getall()[2:-1],
                "links": list(
                    map(lambda href: self.home_url + href[1:], main_category_tags.css("a::attr(href)").getall()[2:-1]))
            })

            for index, name, link in main_categories.itertuples():
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_sub_categories,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "main_category": name
                    }
                )
        except Exception as exception:
            print(exception)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                }
            )

    async def parse_sub_categories(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.wait_for_load_state("networkidle")
            content = await page.content()
            await page.close()

            selector = scrapy.Selector(text=content)
            sub_category_tags = selector.css(".CCollapse-module_cCollapseContent__sR6gM")[0]
            sub_categories = pd.DataFrame({
                "sub_category": sub_category_tags.css("div a::text").getall(),
                "links": list(
                    map(lambda href: self.home_url + href, sub_category_tags.css("div a::attr(href)").getall()))
            })

            for index, name, link in sub_categories.itertuples():
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_product_quantity,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "categories": (response.meta["main_category"], name)
                    }
                )
        except Exception as exception:
            print(exception)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_sub_categories,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "main_category": response.meta["main_category"]
                }
            )

    async def parse_product_quantity(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.wait_for_load_state("networkidle")
            content = await page.content()
            await page.close()

            selector = scrapy.Selector(text=content)
            number_of_pages = ceil(
                int(selector.css(".PLPDesktopHeader_quantityInfoText__4AiWN::text").get().split(" ")[0]) / 20)

            current_page_number = 0
            while current_page_number < number_of_pages:
                current_page_number += 1
                next_page_url = response.url + f"?page={current_page_number}"

                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse_products,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "categories": response.meta["categories"]
                    }
                )
        except Exception as exception:
            print(exception)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_product_quantity,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "categories": response.meta["categories"]
                }
            )

    async def parse_products(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.wait_for_load_state("networkidle")
            content = await page.content()
            await page.close()

            selector = scrapy.Selector(text=content)
            product_cards = selector.css(".PLPProductListing_PLPCardParent__GC2qb")

            for product_card in product_cards:
                main_category, sub_category = response.meta["categories"]
                product_name = product_card.css("h2::text").get()
                product_link = self.home_url + product_card.css("a::attr(href)").get()[1:]
                is_out_of_stock = bool(product_card.css(
                    ".CButton-module_buttonWrapper__rn-B-.CCustomSelect-module_buttonWrapper__CMjV0"
                    ".CButton-module_medium__XbabL.CButton-module_secondary__vR-1m").get())

                if is_out_of_stock:
                    product = MarketItem(
                        main_category=main_category,
                        sub_category=sub_category,
                        lowest_category=sub_category,
                        name=product_name,
                        price=None,
                        high_price=None,
                        in_stock=False,
                        product_link=product_link,
                        page_link=response.url,
                        date=self.current_date
                    )

                    yield product
                    continue
                is_discounted = bool(product_card.css(".CPriceBox-module_discountedPriceContainer__nsaTN").get())
                product_price = float(product_card.css("span.CPriceBox-module_discountedPrice__15Ffw::text").get()
                                      .replace('₺', '').replace('.', '').replace(',', '.')) \
                    if is_discounted else float(product_card.css("span.CPriceBox-module_price__bYk-c::text").get()
                                                .replace('₺', '').replace('.', '').replace(',', '.'))
                product_price_high = float(product_card.css(".CPriceBox-module_price__bYk-c span::text").get()
                                           .replace('₺', '').replace('.', '').replace(',', '.')) \
                    if is_discounted else None

                product = MarketItem(
                    category2=main_category,
                    category1=sub_category,
                    category=sub_category,
                    prod=product_name,
                    price=product_price,
                    high_price=product_price_high,
                    prod_link=product_link,
                    pages=response.url,
                    in_stock=True,
                    date=self.current_date
                )

                yield product
        except Exception as exception:
            print(exception)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_products,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "categories": response.meta["categories"]
                }
            )
