import bs4
import scrapy
import traceback
from ..items import MarketItem
from datetime import date


class MarketpaketiSpider(scrapy.Spider):
    name = "marketpaketi"
    home_url = "https://www.marketpaketi.com.tr"
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

    async def parse(self, response):
        try:
            main_categories = response.css("a.dMenu")

            for main_category in main_categories:
                main_cateory_name = main_category.css("::text").get().strip()
                main_category_link = main_category.css("::attr(href)").get()

                yield scrapy.Request(
                    url=main_category_link,
                    callback=self.parse_sub_categories,
                    meta={
                        "categories": {
                            "main_category": main_cateory_name
                        },
                        "is_lowest_category": False
                    }
                )
        except:
            traceback.print_exc()

    async def parse_sub_categories(self, response):
        try:
            sub_categories = response.css(".uf_blok:nth-child(1) ul.ufb_icerik li a")
            is_lowest_category = response.meta["is_lowest_category"]

            if sub_categories:
                for sub_category in sub_categories:
                    sub_category_name = sub_category.css("::text").get().strip()
                    sub_category_link = sub_category.css("::attr(href)").get()
                    categories = response.meta["categories"]
                    categories["lowest_category" if is_lowest_category else "sub_category"] = sub_category_name

                    yield scrapy.Request(
                        url=sub_category_link,
                        callback=self.parse_page_number if is_lowest_category else self.parse_sub_categories,
                        meta={
                            "categories": categories,
                            "is_lowest_category": True

                        }
                    )
            else:
                categories = response.meta["categories"]
                categories["lowest_category" if is_lowest_category else "sub_category"] = None

                yield scrapy.Request(
                    url=response.url,
                    callback=self.parse_page_number,
                    meta={
                        "categories": categories
                    }
                )
        except:
            traceback.print_exc()

    async def parse_page_number(self, response):
        try:
            total_page_number = self.get_total_page(response)
            current_page = 1

            if total_page_number:
                while current_page <= total_page_number:
                    page_url = response.url + f"?page={current_page}"

                    yield scrapy.Request(
                        url=page_url,
                        callback=self.parse_products,
                        meta={
                            "categories": response.meta["categories"]
                        }
                    )
                    current_page += 1
            else:
                yield scrapy.Request(
                    url=response.url,
                    callback=self.parse_products,
                    meta={
                        "categories": response.meta["categories"]
                    }
                )
        except:
            traceback.print_exc()

    async def parse_products(self, response):
        try:
            product_cards = response.css(".liste_urun")

            if product_cards:
                for product_card in product_cards:
                    product_name = product_card.css("a.urun_adi_ic::text").get().strip()
                    product_link = product_card.css("a.urun_adi_ic::attr(href)").get()
                    product_price, product_price_high = self.get_prices(product_card.get())
                    is_in_stock = bool(product_card.css(".urun_sepet").get())

                    yield MarketItem(
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

    def get_total_page(self, category_page):
        total_page_number = category_page.css(".sayfalama .say::text").getall()

        if total_page_number:
            return int(total_page_number[-1].strip())
        else:
            return None

    def get_prices(self, product_card):
        soup = bs4.BeautifulSoup(product_card, 'html.parser')
        price_tag = soup.find('div', class_='urun_fiyat')

        def sale_price(product_price_tag):
            try:
                return float(product_price_tag.find('strong').next_sibling.strip().strip('TL ').replace(',', '.'))
            except AttributeError:
                try:
                    return float(product_price_tag.text.strip().split()[0].replace(',', '.'))
                except ValueError:
                    try:
                        return float(product_price_tag.find('strong').next_sibling.replace('.', '').replace(',', '.').split()[0])
                    except AttributeError:
                        return float(product_price_tag.text.strip().split()[0].strip('TL ').replace('.', '').replace(',', '.'))
                    finally:
                        return None

            except ValueError:
                try:
                    return float(product_price_tag.find('strong').next_sibling.strip().replace('.', '').replace(',', '.').split()[0])
                except AttributeError:
                    return float(product_price_tag.text.strip().split()[0].strip('TL ').replace('.', '').replace(',', '.'))

        def old_price(product_price_tag):
            try:
                return float(product_price_tag.find('strong').get_text().strip('TL ').replace(',', '.'))
            except AttributeError:
                return None
            except ValueError:
                return float(product_price_tag.find('strong').get_text().strip('TL ').replace('.', '').replace(',', '.'))

        product_price = sale_price(price_tag)
        product_price_high = old_price(price_tag)

        return product_price, product_price_high
