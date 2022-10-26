###### Szenario investigation
import pytest
from py.xml import html # html report for debugging
from pytest_bdd import given, when, then, parsers, scenario, scenarios


#pytest.TEST_URL = "http://dev00.inv.com05.lp.rsint.net"

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
    investigation.login_at_url(url=pytest.TEST_URL)
    page = investigation.page
    # Click  text=TestProceeding1 toggle button for events
    investigation.page.locator("mat-expansion-panel-header[role='button']:has-text('TestProceeding1') >> //ancestor::rs-area  >> rs-toggle-button").first.click()
    # Click eventtable first row that contains the mail class icon
    # Click rs-date-range-select div:has-text("Von") >> nth=3
    page.locator("text=VonBis >> #mat-input-0").fill("")
    # Press Enter
    page.locator("text=VonBis >> #mat-input-0").press("Enter")

    # Click div:nth-child(2) > div:nth-child(4) > rs-data-table-cell > .cell-content
    # Click .cell-content > .ng-star-inserted > .rs-tooltip-trigger > section >> nth=0
    with page.expect_popup() as popup_info:
        investigation.page.locator(".cell-content section:has-text('TestMeasure')  >> //ancestor::section >> //rs-status-icon//i[contains(@class, 'mail')] >> nth=1").click()

    page2 = popup_info.value

    #with investigation.page.expect_popup() as popup_info:
    #   investigation.page.locator("div:nth-child(2) > div:nth-child(4) > rs-data-table-cell > .cell-content").click()
    page2 = popup_info.value
    # Click text=Metadaten
    page2.locator("text=Metadaten").click()

    # Click section:has-text("Identitäten") >> nth=2
    page2.locator("section:has-text(\"Identitäten\")").nth(2).click()
    # Click text=Kennung
    page2.locator("text=Kennung").click()
    # Click text=Anschlussinhaber
    # page2.locator("text=Anschlussinhaber").click()
    # Click text=Hauptsprecher
    # page2.locator("text=Hauptsprecher").click()
    # Click text=IMSI
    #  page2.locator("text=IMSI").click()
    # Click text=IMEI
    # page2.locator("text=IMEI").click()

    # Click span:has-text("EventProduct")
    event_product = page2.locator("rs-attribute[label='Status']").first.inner_text()
                                  #">> div[data-e2e-id='attribute-value']").first.inner_text()
    print(f"Event product: {event_product}")
    # Click text=Inhalt
    assert event_product == "-"
    page2.locator("text=Inhalt").click()
    # Click .cell-content >> nth=0

    # Click text=Kennung
    page2.locator("text=Kennung").click()
    # Click text=Tatsächlicher Teilnehmer
    page2.locator("text=Tatsächlicher Teilnehmer").click()
    # Click th[role="columnheader"]:has-text("IP")
    page2.locator("th[role=\"columnheader\"]:has-text(\"IP\")").click()
    # Click text=Provider
    page2.locator("text=Provider").click()
    # Click text=Ungefährer Standort
    page2.locator("text=Ungefährer Standort").click()
    # Close page
    page2.close()
    # ---------------------

    #pytest.hookimpl(hookwrapper=True)
    #def pytest_runtest_makereport(item, call):
    #    '''data from the output of pytest gets processed here
    #     and are passed to pytest_html_results_table_row'''
    #    outcome = yield
    #    # this is the output that is seen end of test case
    #    report = outcome.get_result()
    #    # taking doc string of the string
    #    column = "New Column"


