# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SokMarketScraperPipeline:
    def process_item(self, item, spider):
        return item


class ReorderFieldsPipeline:
    def process_item(self, item, spider):
        # Define the desired order of fields
        field_order = [
            "main_category",
            "sub_category",
            "lowest_category",
            "name",
            "price",
            "high_price",
            "in_stock",
            "product_link",
            "page_link",
            "date"
        ]
        # Create a new dictionary with the fields in the desired order
        reordered_item = {field: item.get(field) for field in field_order}
        item = reordered_item
        return item
