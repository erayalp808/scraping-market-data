import scrapy
from ..items import MarketItem
from datetime import date
import json


class MigrosSpider(scrapy.Spider):
    name = "migros"
    home_url = "https://www.migros.com.tr/"
    current_date = date.today()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Accept": "application/json",
        "Accept-Language": "tr-TR,tr;q=0.5",
        "X-FORWARDED-REST": "true",
        "X-PWA": "true",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.migros.com.tr/rest/categories",
            meta={
                "playwright": False
            },
            headers=self.headers
        )

    def parse(self, response):
        main_category_datas = json.loads(response.body)["data"][3:]

        for main_category_data in main_category_datas:
            sub_category_datas = main_category_data["children"]

            for sub_category_data in sub_category_datas:
                lowest_category_datas = sub_category_data["children"]

                for lowest_category_data in lowest_category_datas:
                    product_api_endpoint = (f"https://www.migros.com.tr/rest/products/"
                                            f"search?category-id={lowest_category_data['data']['id']}")

                    yield scrapy.Request(
                        url=product_api_endpoint,
                        callback=self.parse_page_count,
                        meta={
                            "playwright": False
                        },
                        headers=self.headers
                    )

    def parse_page_count(self, response):
        total_page_number = int(json.loads(response.body)["data"]["pageCount"])
        for current_page_number in range(1, total_page_number + 1):
            yield scrapy.Request(
                url=response.url + f"&sayfa={current_page_number}&sirala=onerilenler",
                callback=self.parse_products,
                meta={
                    "playwright": False,
                    "page_number": current_page_number
                },
                headers=self.headers
            )

    def parse_products(self, response):
        product_datas = json.loads(response.body)["data"]["storeProductInfos"]

        for product_data in product_datas:
            yield MarketItem(
                main_category=product_data["categoryAscendants"][1]["name"],
                sub_category=product_data["categoryAscendants"][0]["name"],
                lowest_category=product_data["category"]["name"],
                name=product_data["name"],
                price=self.format_price(product_data["salePrice"]),
                high_price=None if product_data["salePrice"] == product_data["regularPrice"]
                else self.format_price(product_data["regularPrice"]),
                in_stock=True,
                product_link=self.home_url + product_data["prettyName"],
                page_link=self.home_url + product_data["category"][
                    "name"] + f"?sayfa={response.meta['page_number']}&sirala=onerilenler",
                date=self.current_date
            )

    def format_price(self, raw_price):
        number_str = str(raw_price)
        formatted_number_str = number_str[:-2] + '.' + number_str[-2:]
        return float(formatted_number_str)
