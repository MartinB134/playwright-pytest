from playwright.sync_api import Page, expect
import re
import pytest
from functools import reduce
from operator import getitem
import time


class Investigation:
    def __init__(self, page: Page):
        self.page = page
        self.testdata = {}  # Permanent Storage in testdata.json will be filled in confest
        self.searchbar = self.page.locator(".nav-search-field input")

    def verify_header(self):
        assert self.page.inner_text('h2') == 'R&S'

    def change_nested_json_values(self,
                                  json_dump: dict = "testdata: {node: {key: value}}",
                                  key_list: list = None,
                                  new_value: str = "") -> str:
        """
        Set item in nested dictionary

        @param json_dump: string in json format that should be traversed
        @param key_list: list with specified values in json. Determines the path of keys.to the value:
        @param new_value: new value that replaces old value
        :return: New Json with changed value at specified key path
        """
        reduce(getitem, key_list[:-1], json_dump)[key_list[-1]] = new_value
        return json_dump
        # return json_dump

    def update_single_product_price(self, product, new_price):
        new_data = self.change_nested_json_values(self.testdata,
                                                  ["products", product, "product_price"],
                                                  new_price)
        self.save_var(new_data)
        return new_data

    def add_price_to_basket_sum(self, price):
        self.testdata["basket"]["sum_value"] += float(str(price).replace(",", "."))

    def selector(self, selector_key="searchbar"):
        if self.__getattribute__(selector_key):
            page_object = self.__getattribute__(selector_key)
            match = re.search(r"selector='(.*)'", page_object.__repr__()).group(1)
        else:
            match = self.page.locator(selector_key)
        return match