import scrapy

from ..items import MarketItem
from datetime import date


class MarketpaketiSpider(scrapy.Spider):
    name = "marketpaketi"
    home_url = "https://www.marketpaketi.com.tr"
    current_date = date.today()

    def start_requests(self):
        yield scrapy.Request(
            url=self.home_url,
            meta={
                "playwright": True,
                "playwright_include_page": True
            }
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.wait_for_load_state("domcontentloaded")
            content = await page.content()
            await page.close()

            selector = scrapy.Selector(text=content)
            main_categories = selector.css(".menu .menu-dropdown-icon")

            for main_category in main_categories:
                main_category_name = main_category.css("a.dMenu::text").get().strip()
                main_category_link = main_category.css("a.dMenu::attr(href)").get()
                sub_categories = main_category.css("ul ul li")[1:]

                for sub_category in sub_categories:
                    sub_category_name = sub_category.css("a::text").get().strip()
                    sub_category_link = sub_category.css("a::attr(href)").get()
                    categories = {
                        "main_category": main_category_name,
                        "sub_category": sub_category_name
                    }

                    yield scrapy.Request(
                        url=sub_category_link,
                        callback=self.parse_lowest_categories,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "categories": categories
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

    async def parse_lowest_categories(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.wait_for_load_state("domcontentloaded")
            content = await page.content()
            await page.close()

            selector = scrapy.Selector(text=content)
            lowest_categories = selector.css(".uf_blok:nth-child(1) ul.ufb_icerik li")

            for lowest_category in lowest_categories:
                lowest_category_name = lowest_category.css("a::text").get().strip()
                lowest_category_link = lowest_category.css("a::attr(href)").get()
                categories = dict(response.meta["categories"], lowest_category=lowest_category_name)

                yield scrapy.Request(
                    url=lowest_category_link,
                    callback=self.parse_products,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "categories": categories
                    }
                )
        except Exception as exception:
            print(exception)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_lowest_categories,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "categories": response.meta["categories"]
                }
            )

    async def parse_products(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.wait_for_load_state("domcontentloaded")
            content = await page.content()
            await page.close()

            selector = scrapy.Selector(text=content)
            product_cards = selector.css(".liste_urun")

            for product_card in product_cards:
                product_name = product_card.css("a.urun_adi_ic::text").get().strip()
                product_link = product_card.css("a.urun_adi_ic::attr(href)").get()
                product_price_high = product_card.css(".urun_fiyat strong::text").get().replace(" TL", '').strip()
                product_price = product_card.css(".urun_fiyat::text").get().replace(" TL", '').strip()
                product_price = product_price.replace(product_price_high, '').strip() \
                    if product_price_high else product_price
                is_in_stock = bool(product_card.css(".urun_sepet").get())

                yield MarketItem(
                    category2=response.meta["categories"]["main_category"],
                    category1=response.meta["categories"]["sub_category"],
                    category=response.meta["categories"]["lowest_category"],
                    prod=product_name,
                    price=product_price,
                    high_price=product_price_high,
                    prod_link=product_link,
                    pages=response.url,
                    in_stock=is_in_stock,
                    date=self.current_date
                )

            next_page_url = self.get_next_page(selector)

            if next_page_url is not None:
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
                callback=self.parse_products,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "categories": response.meta["categories"]
                }
            )

    def get_next_page(self, category_page):
        current_page = category_page.css(".say_aktif::text").get()

        if current_page is not None:
            current_page = int(current_page)
            next_pages = category_page.css(".say ::attr(href)").getall()[1:-1]
            next_pages = next_pages[current_page:]

            if len(next_pages) > 0:
                return next_pages[0]
            else:
                return None
        else:
            return None
