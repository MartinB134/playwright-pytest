###### Szenario Amazon
import allure
import pytest
from pytest_bdd import given, when, then, parsers, scenario

# Todo: remove after alluretest
from functools import partial
#from hamcrest import assert_that
#from allure_commons_test.report import has_test_case
#from allure_commons_test.result import with_status
#from allure_commons_test.result import has_step
## from allure_commons_test.result import has_attachment
#from allure_commons_test.result import has_parameter
#from allure_commons_test.result import has_history_id
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

# Todo: remove after alluretest
def match(matcher, *args):
    for i, arg in enumerate(args):
        if not hasattr(arg, '__call__'):
            matcher = partial(matcher, arg)
        else:
            matcher = partial(matcher, match(arg, *args[i+1:]))
            break
    return matcher()


@allure.step
def show_in_report(arg1, arg2):
    assert arg1 == arg2

# Call other test with this
# scenarios('test_amazon_basket.feature')

@scenario('test_amazon_basket.feature', 'Check the amazon basket for multiple products')
def test_example_is_working_bdd(amazon, page, products: [0.0]):
    single_price_sum = 0.0
    # for product in products.items():
    #    single_price_sum += int(products[product]["product_price"])
    page.locator(amazon.checkout_mini_cart_product_prices)
    assert single_price_sum == 0.0

@allure.severity(allure.severity_level.MINOR)
@given(parsers.parse('I find and add the cheapest product to the basket'))
def seek_low_priced_product(products, page, amazon, write_testdata_to_current_page_class, helpers):
    print(f"What is page? :  {page}")
    if amazon.reject_cookies.is_visible():
        amazon.reject_cookies.click()
    for i, product in enumerate(products):  # could also be parametrized in fixture
        match = amazon.selector("searchbar")
        print(f"From Products: {products} \n"
              f"Evaluating Product: '{product}'\n"
              f"match: {match}")
        page.wait_for_url(f"{pytest.Amazon_URL}*")
        page.wait_for_timeout(500)
        page.wait_for_selector(".nav-search-field input")
        page.is_visible(".nav-search-field input")
        # Search for specific product
        page.fill(".nav-search-field input", str(product))
        # Press Enter and wait page to load completely
        page.locator("input[name=\"field-keywords\"]").press("Enter")
        page.wait_for_url(f"{pytest.Amazon_URL}/s?k=*{product}*")
        amazon.sort_for_product_price_asc(product)
        locator_cheapest_price, product_price = amazon.choose_best_priced_product_from_results(product)
        print(f"product_price: '{product_price}' \n"
              f"Pytest database: {pytest.initial_testdata}\n"
              f"Amazon Testdata:\n {amazon.testdata}")
        # write_price_to_products(product_price, product)
        # new_data = amazon.change_nested_json_values(amazon.testdata,
        #                                             ["products", product, "product_price"],
        #                                             product_price)
        # amazon.save_var(new_data)
        amazon.update_single_product_price(product, product_price)
        # amazon.sum_basket(product_price)
        var = amazon.basket()
        var2 = var['sum_value']
        print(f"Amazon.basket(): {var}")
        print(f"Amazon. Get_Var('products'): {amazon.get_var('products')}")
        locator_cheapest_price.click()
        amazon.add_product_to_basket(product)
        # amazon.add_price_to_basket_sum(product_price)


@when(parsers.parse('all products are added to the basket'))
def check_mini_basket(page, amazon):
    minibasket_price = amazon.page.locator("//*[contains(@class, 'subtotal-value')]").inner_text()
    products = amazon.products()
    basket = amazon.basket()
    print(f"Amazon products: {products} \n "
          f"Basket: {basket} \n "
          f"Minibasket_price: {minibasket_price}")


@allure.step('I can describe and also display parameters of the called function: amazon.product_price_options:"{amazon.product_price_options}"')
@then(parsers.parse('Products are displayed with added sums in basket'), target_fixture='product_price')
def check_sum_in_basket(page, amazon, extra):
    amazon.cart_toggle.click()
    added_products_sum = str(amazon.basket()['sum_value'])
    print(f"Basket final: {added_products_sum}")
    amazon.basket_total.wait_for()
    ### Reporting Test
    allure.attach(amazon.page.screenshot())
    extra.append(extras.text("some string MB. Check_sum_in_basket"))

    #### Reporting Test
    displayed_sum = amazon.basket_total.text_content()[1:]
    assert added_products_sum == displayed_sum


@then("Going to checkout leads to login")
def step_impl(amazon):
    amazon.checkout_basket.click()
    amazon.page.wait_for_url(f"{pytest.Amazon_URL}*")
    assert amazon.page.locator("h1 >> text=Sign in").is_visible()
    # raise NotImplementedError(u'STEP: But Going to checkout is not possible without login')
