###### Szenario Amazon
import allure
import pytest
from pytest_bdd import given, when, then, parsers, scenario, scenarios

from pytest_html import extras

pytest.TEST_URL = "http://dev00.inv.com05.lp.rsint.net"

# Call other tests like this:
scenarios('test_Kommunikationsdetails_gdm_for_identities.feature')

@scenario('test_Kommunikationsdetails_gdm_for_identities.feature', 'Check Identities GDM for Phone Calls')
def run_scenario():
    pass  # inser tlast assertion here

@given(parsers.parse("I opened a DdeA for a phone call communication event"), target_fixture="page")
def navigate_to_url(investigation):
    investigation.page.goto(f"{pytest.TEST_URL}")

@then(parsers.parse('the following attributes out of the GDM are added / adjusted to the widget'))
def check_fields(investigation, helpers):
    helpers.write_testdata_to_current_page_class(investigation)
    # page = return_test_page
    # Go to http://eqa02.inv.com05.lp.rsint.net/#/investigation/
    #page.goto("http://dev05.inv.com05.lp.rsint.net/#/investigation/")
    # input username
    investigation.page.locator("input[id=\"username\"]").click()
    # Fill input[name="username"]
    investigation.page.locator("input[id=\"username\"]").fill("investigator")
    # Click input[name="password"]
    investigation.page.locator("input[name=\"password\"]").click()
    # Fill input[name="password"]
    investigation.page.locator("input[name=\"password\"]").fill("investigator")
    # Click input:has-text("Sign In")
    investigation.page.locator("input:has-text(\"Sign In\")").click()
    investigation.page.wait_for_url("*.inv.com05.lp.rsint.net*")
    # Click text=TestProceeding1 (AZ-JS20190822) 15 >> button
    investigation.page.locator(".cell-content section:has-text('TestMeasure')  >> //ancestor::section >> "
                               "//rs-status-icon//i[contains(@class, 'mail')] >> nth=1").click()
    # Click div:nth-child(2) > div:nth-child(4) > rs-data-table-cell > .cell-content
    with investigation.page.expect_popup() as popup_info:
        investigation.page.locator("div:nth-child(2) > div:nth-child(4) > rs-data-table-cell > .cell-content").click()
    page1 = popup_info.value
    # Click text=Metadaten
    page1.locator("text=Metadaten").click()
    page1.locator("div:nth-child(7) > div:nth-child(3) > rs-data-table-cell > .cell-content").first.click()
    page1 = popup_info.value
    # Click section:has-text("Identitäten") >> nth=2
    page1.locator("section:has-text(\"Identitäten\")").nth(2).click()
    # Click text=Kennung
    page1.locator("text=Kennung").click()
    # Click text=Anschlussinhaber
    page1.locator("text=Anschlussinhaber").click()
    # Click text=Hauptsprecher
    page1.locator("text=Hauptsprecher").click()
    # Click text=IMSI
    page1.locator("text=IMSI").click()
    # Click text=IMEI
    page1.locator("text=IMEI").click()

    # Click mat-select[role="combobox"] >> text=Schnellfilter
    investigation.page1.locator("mat-select[role=\"combobox\"] >> text=Schnellfilter").click()
    # Click span:has-text("EventProduct")
    event_product = investigation.page1.locator("span:has-text(\"EventProduct\")").first().getText()
    print(f"Event product: {event_product}")
    # Click text=Inhalt
    investigation.page1.locator("text=Inhalt").click()
    # Close investigation.page
    investigation.page1.close()
    # Click .cell-content >> nth=0
    with investigation.page.expect_popup() as popup_info:
        investigation.page.locator(".cell-content").first.click()
    investigation.page2 = popup_info.value
    # Click text=Kennung
    investigation.page2.locator("text=Kennung").click()
    # Click text=Tatsächlicher Teilnehmer
    investigation.page2.locator("text=Tatsächlicher Teilnehmer").click()
    # Click th[role="columnheader"]:has-text("IP")
    investigation.page2.locator("th[role=\"columnheader\"]:has-text(\"IP\")").click()
    # Click text=Provider
    investigation.page2.locator("text=Provider").click()
    # Click text=Ungefährer Standort
    investigation.page2.locator("text=Ungefährer Standort").click()
    # Close investigation.page
    investigation.page2.close()
    # ---------------------

    investigation.page.wait_for_url(f"{pytest.Amazon_URL}*")
    # amazon.investigation.page.click(searchbar)
    # Search for specific product
    #investigation.page.fill(searchbar, str(product))
    # Press Enter and wait investigation.page to load completely
    #investigation.page.locator(searchbar).press("Enter")
    #investigation.page.wait_for_url(f"{pytest.Amazon_URL}/s?k=*{product}*")
    # amazon.sort_for_product_price_asc(product)


@when(parsers.parse('all products are added to the basket'))
def check_mini_basket(page, amazon):
    minibasket_price = amazon.investigation.page.locator("//*[contains(@class, 'subtotal-value')]").inner_text()
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
    #show_in_report(added_products_sum, displayed_sum)
    assert added_products_sum == displayed_sum


@then("Going to checkout leads to login")
def step_impl(amazon):
    amazon.checkout_basket.click()
    amazon.page.wait_for_url(f"{pytest.Amazon_URL}*")
    assert amazon.page.locator("h1 >> text=Sign in").is_visible()

