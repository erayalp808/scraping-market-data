import traceback

import scrapy
from math import ceil
from ..items import MarketItem
from datetime import date


class SokmarketSpider(scrapy.Spider):
    name = "sokmarket"
    current_date = date.today()
    home_url = "https://www.sokmarket.com.tr/"
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
        },
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        }
    }

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
            main_category_tags = selector.css(".CategoryList_categories__wmXtl")[0].css("a")

            for main_category_tag in main_category_tags:
                main_category_name = main_category_tag.css("span::text").get().strip()
                main_category_link = self.home_url + main_category_tag.css("::attr(href)").get()[1:]

                yield scrapy.Request(
                    url=main_category_link,
                    callback=self.parse_sub_categories,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "main_category": main_category_name
                    }
                )
        except:
            traceback.print_exc()
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
            sub_category_tags = selector.css(".CCollapse-module_cCollapseContent__sR6gM")[0].css("div a")

            for sub_category_tag in sub_category_tags:
                sub_category_name = sub_category_tag.css("::text").get().strip()
                sub_category_link = self.home_url + sub_category_tag.css("::attr(href)").get()

                yield scrapy.Request(
                    url=sub_category_link,
                    callback=self.parse_product_quantity,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "categories": (response.meta["main_category"], sub_category_name)
                    }
                )
        except:
            traceback.print_exc()
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
        except:
            traceback.print_exc()
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
                    yield MarketItem(
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
                    continue
                is_discounted = bool(product_card.css(".CPriceBox-module_discountedPriceContainer__nsaTN").get())
                product_price = float(product_card.css("span.CPriceBox-module_discountedPrice__15Ffw::text").get()
                                      .replace('₺', '').replace('.', '').replace(',', '.')) \
                    if is_discounted else float(product_card.css("span.CPriceBox-module_price__bYk-c::text").get()
                                                .replace('₺', '').replace('.', '').replace(',', '.'))
                product_price_high = float(product_card.css(".CPriceBox-module_price__bYk-c span::text").get()
                                           .replace('₺', '').replace('.', '').replace(',', '.')) \
                    if is_discounted else None

                yield MarketItem(
                    main_category=main_category,
                    sub_category=sub_category,
                    lowest_category=sub_category,
                    name=product_name,
                    price=product_price,
                    high_price=product_price_high,
                    in_stock=True,
                    product_link=product_link,
                    page_link=response.url,
                    date=self.current_date
                )
        except:
            traceback.print_exc()
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_products,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "categories": response.meta["categories"]
                }
            )
