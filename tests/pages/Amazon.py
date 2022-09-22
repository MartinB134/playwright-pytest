# POM model to keep selectors maintainable
import json

from playwright.sync_api import Page, expect
import re
import pytest
from functools import reduce
from operator import getitem


class Amazon:
    def __init__(self, page: Page):
        self.page = page
        # Data from TESTDATA_PATH = "tests/assets/testdata.json"
        self.testdata = {}  # Permanent Storage in testdata.json
        self.searchbar = self.page.locator(".nav-search-field input")
        self.reject_cookies = self.page.locator("//a[contains(@id, 'rejectall')]")
        self.sort_select_toggle = self.page.locator("//select[contains(@id, 'result-sort')]/../span")
        self.sort_option_ascending = self.page.locator(
            "//div[contains(@id, 'popover')]//a[contains(text(), 'aufsteigend') or contains(text(), \"Low to High\")]")
        self.first_deliverable_product_text = self.page.locator(
            "((//*[contains(@aria-label, 'Lieferung') or contains(@aria-label, 'Get it')])[1]//ancestor::*[@data-asin]//h2)[1]")
        self.first_deliverable_product_price = self.page.locator(
            "(//*[contains(@aria-label, 'Lieferung') or contains(@aria-label, 'Get it')]"
            "//ancestor::*[@data-asin]//*[contains(@class, 'price-whole')])[1]")
        self.product_texts = self.page.locator(
            "(//*[contains(@aria-label, '')])[1]//ancestor::*[@data-asin]//h2")
        self.deliverable_product_prices = self.page.locator(
            "//*[contains(@aria-label, 'Get it') or contains(@aria-label, 'Lieferung')]"
            "//ancestor::*[@data-asin]//*[contains(@class, 'price-whole')]")
        self.deliverable_product_price_fractions = self.page.locator(
            "//*[contains(@aria-label, 'Lieferung') or contains(@aria-label, 'Get it')]"
            "//ancestor::*[@data-asin]//*[contains(@class, 'price-fraction')]")
        self.next_button = self.page.locator("//*[contains(@class, 'pagination')]//a[contains(@class, 'next')]")
        self.add_to_basket_impossible = self.page.locator("#exportsUndeliverable-cart-announce")
        self.checkout_mini_cart_product_prices = self.page.locator(
            "//*[contains(@data-cart-type,'Retail_Cart')]//*[contains(@class, 'unit-price')]")
        self.checkout_mini_cart = self.page.locator(
            "//*[contains(@data-cart-type,'Retail_Cart')]//*[@data-price]")
        self.product_price_options = self.page.locator("//*[contains(@id,'variation_')]/ul")  # If this is visible, get cheapest
        self.product_price_options_inner = self.page.locator("//*[contains(@id,'variation_')]/ul/li//span")  # If this is visible, get cheapest
        self.product_price_single = self.page.locator("//*[@id= 'newAccordionRow']//*[contains(@class, 'a-price')][1]")
        self.product_price_alternative = self.page.locator("(//h5//*[contains(@class, 'text-price')]/span)[1]")
        self.buy_button_alt = self.page.locator(
            "//*[@id= 'mbc']//span[contains(@class, 'primary')]"
            "//*[contains(text(), 'Basket') or contains(text(), 'Einkaufswagen')]")
        self.cart_toggle = self.page.locator("#nav-cart")
        self.checkout_basket = self.page.locator("//*[contains(@id, 'buy-box')]//input[contains(@type, 'submit')]")
        self.basket_total = self.page.locator("(//span[contains(@id, 'subtotal-amount')]//*[contains(@class, 'sc-price')])[1]")
        self.single_product_basket_price = self.page.locator(".a-section span.apexPriceToPay")

    #########################################
    #   Combined functions
    #################################
    def verify_header(self):
        assert self.page.inner_text('h2') == 'Amazon'

    def sort_for_product_price_asc(self, product: str) -> None:
        # page = amazon_page
        # Click Toggle Sort
        self.sort_select_toggle.click()
        # Click selection price Ascending
        self.sort_option_ascending.click()
        self.page.wait_for_url(f"{pytest.Amazon_URL}/s?k={product}*")

    def choose_best_priced_product_from_results(self, product):
        self.page.wait_for_url(f"{pytest.Amazon_URL}/s?k={product}*")
        # Wait for the product text and prices to e visible
        self.product_texts.first.wait_for(timeout=6000)
        self.first_deliverable_product_price.wait_for(timeout=2000)
        # self.page.wait_for_timeout(2000)
        while not self.first_deliverable_product_price.is_visible():
            self.next_button.click()
            print(f"Clicked on next in product search: '{product}'")
            self.product_texts.first.wait_for(timeout=6000)
        self.deliverable_product_prices.first.wait_for(timeout=6000)
        lowest_price = self.return_cheapest_price_from_product_overview()
        print(f"Lowest Price identified: '{lowest_price}'")
        locator_cheapest_product = self.page.locator(
            f"//span[contains(@class, 'a-price')]//*[contains(text(), '{lowest_price}') "
            f"or contains(text(), '{lowest_price.replace('.', ',')}')]/..").first
        return locator_cheapest_product, lowest_price

    def return_cheapest_price_from_product_overview(self):
        self.page.wait_for_timeout(1000)
        price_wholes = self.deliverable_product_prices.all_inner_texts()  # e.g. ['10\n,', '8\n,', '15\n,']
        price_fractions = self.deliverable_product_price_fractions.all_inner_texts()  # e.g. ['99', '49', '33']
        price_wholes = [price[:-2] for price in price_wholes]  # cut off the last three unnecessary digits
        final_prices = []
        for index, item in enumerate(price_fractions):
            try:
                final_prices.append(price_wholes[index] + "." + item)
            except IndexError as error_msg:
                print(f"Number of fractions '{len(price_fractions)}' does not match number of whole prices: "
                      f"'{price_wholes.__len__()}'. Errormsg:{error_msg}")
        final_prices_float = [float(price) for price in final_prices]
        final_prices_float.sort()
        print(f"Final prices: {final_prices_float}")
        lowest_price = str(final_prices_float[0])  # for germany .replace(".", ",")
        print(f"Lowest Price found: {lowest_price}")
        return lowest_price

    def add_product_to_basket(self, product):
        # Click Add to Cart button
        # Click input:has-text("In den Einkaufswagen")
        self.page.wait_for_url(f"{pytest.Amazon_URL}/*")
        if self.add_to_basket_impossible.is_visible():
            product_price = self.product_price_alternative.inner_text()
            self.buy_button_alt.click()
            self.add_price_to_basket_sum(product_price)
        if self.page.locator("//a[.//span[contains(text(), 'One-time purchase') "
                             "or contains(text(), 'Einmalkauf')]]").is_visible():
            self.page.locator("//a[.//span[contains(text(), 'One-time purchase') "
                              "or contains(text(), 'Einmalkauf')]]").click()
            product_price = self.product_price_alternative.inner_text()[1:]
            self.page.locator("form input#add-to-cart-button").click()
            #self.add_price_to_basket_sum(product_price)
        else:
            # product_price = self.page.locator("#corePrice_feature_div .a-price >> nth=1").inner_text() not concise
            self.page.locator("form input#add-to-cart-button").click()

        self.page.wait_for_url(f"{pytest.Amazon_URL}/*")
        # Click text=Proceed to checkout Zur Kasse gehen Zur Kasse >> input[name="proceedToCheckout"]
        # self.page.locator("input[name=\"proceedToCheckout\"]").click()
        self.checkout_mini_cart.first.wait_for()  # self.checkout_mini_cart_product_prices.first.wait_for()

    ####################
    # Helper functions
    ####################
    def save_var(self, variable: dict):
        self.testdata.update(variable)

    def get_var(self, key):
        return self.testdata[key]

    def basket(self):
        print(f"IN BASKET: {self.testdata}")
        return self.testdata["basket"]

    def products(self):
        return self.testdata["products"]

    def sum_basket(self, price):
        self.testdata["basket"]["sum_value"] += float(str(price).replace(",", "."))

    '''
    def products(testdata):
        return testdata["products"]
    '''
    def change_nested_json_values(self,
                                  json_dump: str = "testdata: {node: {key: value}}",
                                  key_list: list = None,
                                  new_value: str = "") -> str:
        """Set item in nested dictionary

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

    def add_price_to_basket_sum(self, price: (float | str)):
        self.testdata["basket"]["sum_value"] += float(str(price).replace(",", "."))
        print(f"Value: {price} added to basket: {self.testdata['basket']['sum_value']}")
        # self.change_nested_json_values(json.dumps(self.testdata),
        #                               ["basket", "sum_value"],
        #                               new_basket_price)

    def selector(self, amazon_selector="searchbar"):
        if self.__getattribute__(amazon_selector):
            page_object = self.__getattribute__(amazon_selector)
            match = re.search(r"selector='(.*)'", page_object.__repr__()).group(1)
        else:
            match = self.page.locator(amazon_selector)
        return match

