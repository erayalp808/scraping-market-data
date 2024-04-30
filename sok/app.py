from typing import List

import bs4
import pandas as pd
from numpy import nan
from math import ceil

from helper import get_content, current_date, create_directory, path_base

create_directory()


def get_main_categories(url: str) -> pd.DataFrame:
    if url is nan:
        main_category_tags = [nan]
        main_category_names = [nan]
        main_category_links = [nan]
    else:
        content = get_content(url)
        main_category_tags = get_main_category_tags(content)
        main_category_names = get_category_names(main_category_tags)
        main_category_links = get_category_links(main_category_tags)
        return pd.DataFrame({'name': main_category_names, 'link': main_category_links})


def get_sub_categories(url: str) -> pd.DataFrame:
    if url is nan:
        sub_category_tags = [nan]
        sub_category_names = [nan]
        sub_category_links = [nan]
    else:
        content = get_content(url)
        sub_category_tags = get_sub_category_tags(content)
        sub_category_names = get_category_names(sub_category_tags)
        sub_category_links = get_category_links(sub_category_tags)
        return pd.DataFrame({'name': sub_category_names, 'link': sub_category_links})


def get_main_category_tags(content: bs4.Tag) -> list[bs4.Tag] | float:
    main_category_wrapper: bs4.Tag = content.findAll('div', class_='CategoryList_categories__wmXtl')[1]
    main_category_tags = list(main_category_wrapper.findAll('a')[2:-1])
    if not main_category_tags:
        return nan
    return main_category_tags


def get_sub_category_tags(content: bs4.Tag) -> list[bs4.Tag] | float:
    sub_category_wrapper: bs4.Tag = content.findAll('div', class_='CCollapse-module_cCollapseContent__sR6gM')[0]
    sub_category_tags = list(sub_category_wrapper.findAll('a'))
    if not sub_category_tags:
        return nan
    return sub_category_tags


def get_category_links(category_tags: list[bs4.Tag]) -> list[float] | list[str]:
    if category_tags is nan:
        return [nan]
    category_links = [MAIN_URL + a['href'] for a in category_tags]
    return category_links


def get_category_names(category_tags: list[bs4.Tag]) -> list[float] | list[str]:
    if category_tags is nan:
        return [nan]
    category_names = [a.text.strip() for a in category_tags]
    return category_names


MAIN_URL = "https://www.sokmarket.com.tr"

main_category = get_main_categories(MAIN_URL)
sub_categories = {}

for index, name, link in main_category.itertuples():
    sub_categories[name] = get_sub_categories(link)