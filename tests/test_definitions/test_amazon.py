###### Szenario Amazon
import allure
import pytest
from pytest_bdd import given, when, then, parsers, scenario

from pytest_html import extras

EXTRA_TYPES = {
    'Number': int,
    'String': str
}

CONVERTERS = {
    'initial': int,
    'product': str,
    'some': int,
    'total': int,
}


@allure.step
def show_in_report(arg1, arg2):
    pass


# Call other tests like this:
# scenarios('test_amazon_basket.feature')

@scenario('test_amazon_basket.feature', 'Check the amazon basket for multiple products')
def test_run(amazon, page, products: [0.0]):
    pass


@allure.severity(allure.severity_level.MINOR)
@given(parsers.parse('I find and add the cheapest product to the basket'))
def seek_low_priced_product(products, page, amazon, helpers):
    helpers.write_testdata_to_current_page_class(amazon)
    if amazon.reject_cookies.is_visible():
        amazon.reject_cookies.click()
    for i, product in enumerate(products):  # could also be parametrized in fixture @pytest.mark.parameterize
        searchbar = amazon.selector("searchbar")
        page.wait_for_url(f"{pytest.Amazon_URL}*")
        amazon.page.click(searchbar)
        # Search for specific product
        page.fill(searchbar, str(product))
        # Press Enter and wait page to load completely
        page.locator(searchbar).press("Enter")
        page.wait_for_url(f"{pytest.Amazon_URL}/s?k=*{product}*")
        amazon.sort_for_product_price_asc(product)
        locator_cheapest_price, product_price = amazon.choose_best_priced_product_from_results(product)
        amazon.update_single_product_price(product, product_price)
        locator_cheapest_price.click()
        amazon.add_product_to_basket(product)


@when(parsers.parse('all products are added to the basket'))
def check_mini_basket(page, amazon):
    minibasket_price = amazon.page.locator("//*[contains(@class, 'subtotal-value')]").inner_text()
    products = amazon.products
    basket = amazon.basket()
    print(f"Basket: {basket} \n "
          f"Minibasket_price: {minibasket_price}")


@then(parsers.parse('Products are displayed with added sums in basket'), target_fixture='product_price')
def check_sum_in_basket(page, amazon, extra):
    amazon.cart_toggle.click()
    # Get added up value from the generated testrun and round it like amazon does
    added_products_sum = str("%.2f" % round(amazon.basket()['sum_value'], 2))
    print(f"Basket final: {added_products_sum}")
    amazon.basket_total.wait_for()
    # Attach Screenshot of final basket in allure report
    allure.attach(amazon.page.locator(selector='div', has_text="Shopping Cart").first.screenshot())
    extra.append(extras.text("In function. Check_sum_in_basket"))
    displayed_sum = amazon.basket_total.text_content()[1:]  # Cut the currency in front of the value and return the text
    show_in_report(added_products_sum, displayed_sum)
    assert added_products_sum == displayed_sum


@then("Going to checkout leads to login")
def step_impl(amazon):
    amazon.checkout_basket.click()
    amazon.page.wait_for_url(f"{pytest.Amazon_URL}*")
    assert amazon.page.locator("h1 >> text=Sign in").is_visible()

