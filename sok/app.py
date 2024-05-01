from typing import List, Tuple

import bs4
import pandas as pd
from numpy import nan
from math import ceil

from helper import get_content, current_date, create_directory, path_base

create_directory()


def get_main_categories(url: str) -> pd.DataFrame:
    if url is nan:
        main_category_names = [nan]
        main_category_links = [nan]
        return pd.DataFrame({'name': main_category_names, 'link': main_category_links})
    else:
        content = get_content(url)
        main_category_tags = get_main_category_tags(content)
        main_category_names = get_category_names(main_category_tags)
        main_category_links = get_main_category_links(main_category_tags)
        return pd.DataFrame({'name': main_category_names, 'link': main_category_links})


def get_sub_categories(url: str) -> pd.DataFrame:
    if url is nan:
        sub_category_names = [nan]
        sub_category_links = [nan]
        return pd.DataFrame({'name': sub_category_names, 'link': sub_category_links})
    else:
        content = get_content(url)
        sub_category_tags = get_sub_category_tags(content)
        sub_category_names = get_category_names(sub_category_tags)
        sub_category_links = get_sub_category_links(sub_category_tags)
        return pd.DataFrame({'name': sub_category_names, 'link': sub_category_links})


def get_main_category_tags(content: bs4.Tag) -> List[bs4.Tag] | float:
    main_category_wrapper: bs4.Tag = content.findAll('div', class_='CategoryList_categories__wmXtl')[1]
    main_category_tags = list(main_category_wrapper.findAll('a')[2:-1])
    if not main_category_tags:
        return nan
    return main_category_tags


def get_sub_category_tags(content: bs4.Tag) -> List[bs4.Tag] | float:
    sub_category_wrapper: bs4.Tag = content.findAll('div', class_='CCollapse-module_cCollapseContent__sR6gM')[0]
    sub_category_tags = list(sub_category_wrapper.findAll('a'))
    if not sub_category_tags:
        return nan
    return sub_category_tags


def get_main_category_links(main_category_tags: List[bs4.Tag]) -> List[float] | List[str]:
    if main_category_tags is nan:
        return [nan]
    main_category_links = [MAIN_URL + a['href'] for a in main_category_tags]
    return main_category_links


def get_sub_category_links(sub_category_tags: List[bs4.Tag]) -> List[float] | List[str]:
    if sub_category_tags is nan:
        return [nan]
    sub_category_links = [MAIN_URL + '/' + a['href'] for a in sub_category_tags]
    return sub_category_links


def get_category_names(category_tags: List[bs4.Tag]) -> List[float] | List[str]:
    if category_tags is nan:
        return [nan]
    category_names = [a.text.strip() for a in category_tags]
    return category_names


MAIN_URL = "https://www.sokmarket.com.tr"

main_category = get_main_categories(MAIN_URL)
sub_categories = {}

for index, name, link in main_category.itertuples():
    sub_categories[name] = get_sub_categories(link)


def get_products(url, category2, category1) -> pd.DataFrame:
    try:
        content = get_content(url)
        number_of_pages = ceil(get_product_quantity(content) / 20)
        product_datas: List[pd.DataFrame] = []

        for page in range(number_of_pages):
            product_page_url = url + f'?page={page + 1}'
            product_page_content = get_content(product_page_url)
            product_cards: list[bs4.Tag] = get_product_cards(product_page_content)
            product_names = list(map(lambda product_card: get_product_name(product_card), product_cards))
            product_links = list(map(lambda product_card: get_product_link(product_card), product_cards))
            product_prices = list(map(lambda product_card: get_product_prices(product_card)[0], product_cards))
            product_prices_high = list(map(lambda product_card: get_product_prices(product_card)[1], product_cards))
            product_page_data = pd.DataFrame({
                "category2": category2,
                "category1": category1,
                "category": category1,
                "name": product_names,
                "price": product_prices,
                "price_high": product_prices_high,
                "link": product_links,
                "page": product_page_url
            })
            product_datas.append(product_page_data)

        merged_data = pd.DataFrame({
            "category2": [],
            "category1": [],
            "category": [],
            "name": [],
            "price": [],
            "price_high": [],
            "link": [],
            "page": []
        })

        for product_data in product_datas:
            merged_data = pd.concat([merged_data, product_data], axis=0, ignore_index=True)

        return merged_data
    except:
        print(f"page: {url} not loaded")


def get_product_cards(content: bs4.Tag) -> List[bs4.Tag]:
    product_cards_wrapper: bs4.Tag = content.find('div', class_='PLPProductListing_PLPCardsWrapper__POow2')
    product_cards: list[bs4.Tag] = product_cards_wrapper.findAll('div', class_='PLPProductListing_PLPCardParent__GC2qb')
    return product_cards


def get_product_quantity(content: bs4.Tag) -> int:
    return int(content.find('p', class_='PLPDesktopHeader_quantityInfoText__4AiWN').text.split()[0])


def get_product_name(content: bs4.Tag) -> str:
    return content.find('h2', class_='CProductCard-module_title__u8bMW').text.strip()


def get_product_prices(content: bs4.Tag) -> Tuple[float, float]:
    price_tag = content.find(class_='CPriceBox-module_price__bYk-c')
    price = float(price_tag.text.strip().replace('₺', '').replace('.', '').replace(',', '.'))
    sale_price_tag = content.find('span', class_='CPriceBox-module_discountedPrice__15Ffw')

    if sale_price_tag:
        sale_price = float(sale_price_tag.text.strip().replace('₺', '').replace('.', '').replace(',', '.'))
        return sale_price, price
    else:
        return price, nan


def get_product_link(content: bs4.Tag) -> str:
    return MAIN_URL + content.find('a')['href']


final_data = pd.DataFrame({
    "category2": [],
    "category1": [],
    "category": [],
    "name": [],
    "price": [],
    "price_high": [],
    "link": [],
    "page": []
})

for key in sub_categories.keys():
    for index, name, link in sub_categories[key].itertuples():
        final_data = pd.concat([final_data, get_products(link, key, name)], axis=0, ignore_index=True)

path_file = path_base + 'data/' + current_date + '.csv'

final_data.to_csv(path_file, index=False)
