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
# Saved for later use:
# helpers.write_testdata_to_current_page_class(page_name)

@scenario('test_amazon_basket.feature', 'Check the amazon basket for multiple products')
def test_run(amazon, page, products: [0.0]):
    pass


@given(parsers.parse("A browser is opened at page amazon"), target_fixture="page")
def return_amazon_page(amazon):
    print(f"Amazon called")
    amazon.page.context.tracing.start(screenshots=True, snapshots=True)
    amazon.page.goto(f"{pytest.EXAMPLE_URL}")
    return amazon.page

# @given("A browser is opened at page amazon")
# def step(amazon):
#     print(f"Loggin in")
#     amazon.login_at_url(pytest.EXAMPLE_URL)
#     amazon.page.goto(f"{pytest.EXAMPLE_URL}")
#     # raise NotImplementedError(u'STEP: Given A browser is opened at page amazon')


@allure.severity(allure.severity_level.MINOR)
@given(parsers.parse('I find and add the cheapest product to the basket'))
def seek_low_priced_product(products, page, amazon, helpers):
    helpers.write_testdata_to_current_page_class(amazon)
    if amazon.reject_cookies.is_visible():
        amazon.reject_cookies.click()
    for i, product in enumerate(products):  # could also be parametrized in fixture @pytest.mark.parameterize
        searchbar = amazon.selector("searchbar")
        page.wait_for_url(f"*{pytest.EXAMPLE_URL}*")
        amazon.page.click(searchbar)
        # Search for specific product
        page.fill(searchbar, str(product))
        # Press Enter and wait page to load completely
        page.locator(searchbar).press("Enter")
        page.wait_for_url(f"*{pytest.EXAMPLE_URL}/s?k=*{str(product).replace(' ', '+')}*")
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
    amazon.page.wait_for_url(f"*{pytest.EXAMPLE_URL}*")
    assert amazon.page.locator("h1 >> text=Sign in").is_visible()


@given(parsers.parse("Zipcode is set the US address {zipcode}"))
def change_zipcode_us(zipcode, amazon=return_amazon_page):
    # Click locator to change address
    amazon.page.wait_for_url(f"*{pytest.EXAMPLE_URL}*")
    # Anomaly where the amazon page starts at a different state
    if amazon.page.locator("a:has-text('Departments')").is_visible():
        # Reset Page
        amazon.page.locator("text=Departments").first.click()
    # Sometimes amazon starts at a different amazon home page
    if not amazon.page.locator('//*[contains(@id,"nav-pack")]').is_visible():
        amazon.page.goto(f"{pytest.EXAMPLE_URL}")
    amazon.page.locator('//*[contains(@id,"nav-pack")]').click()
    amazon.page.locator('[aria-label="oder gib eine US-Postleitzahl an"]').click()
    # Fill [aria-label="oder geben Sie eine US-Postleitzahl an"]
    amazon.page.locator('[aria-label="oder gib eine US-Postleitzahl an"]').fill(zipcode)
    amazon.page.locator("div[id='GLUXSpecifyLocationDiv'] .a-button-input").click()
    # Click text=BestätigenBitte gültige Postleitzahl eingebenDiese Postleitzahl ist derzeit nich >> input[type="submit"]
    # amazon.page.locator("text=BestätigenBitte gültige Postleitzahl eingebenDiese Postleitzahl ist derzeit nich >> input[type=\"submit\"]").click()
    # Click confirm button
    if amazon.page.locator('.a-popover-footer input').is_enabled():
        amazon.page.locator('.a-popover-footer input').click()
    # Click second confirm button
    # amazon.page.locator(".a-popover-footer input").click()
