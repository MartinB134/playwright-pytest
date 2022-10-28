###### Szenario investigation
import allure
import pytest
from playwright.sync_api import expect
from playwright.sync_api import Page as page
from py.xml import html  # html report for debugging
from pytest_bdd import given, when, then, parsers, scenario, scenarios
EXTRA_TYPES = {
    'Number': int,
    'String': str
}


#pytest.TEST_URL = "http://dev00.inv.com05.lp.rsint.net"

# Call other tests like this:
scenarios('test_Kommunikationsdetails_gdm_for_identities_outline.feature')


@scenario('test_Kommunikationsdetails_gdm_for_identities_outline.feature', 'Check Identities GDM for multiple Event Types')
def run_scenario():
    pass  # insert last assertion here


@given(parsers.parse("I opened a DdeA for a {communication_event}"), target_fixture="page")
def return_page(investigation, communication_event):
    print(f"Communication event")
    investigation.page.goto(f"{pytest.TEST_URL}")
    return investigation.page


@then(parsers.parse('the following {attributes} out of the GDM are added / adjusted to the widget'))
def check_fields(investigation, helpers):
    helpers.write_testdata_to_current_page_class(investigation)
    investigation.login_at_url(url=pytest.TEST_URL)
    # Click  text=TestProceeding1 toggle button for events
    investigation.page.locator("mat-expansion-panel-header[role='button']:has-text('TestProceeding1') >> //ancestor::rs-area  >> rs-toggle-button").first.click()
    # Click eventtable first row that contains the mail class icon
    # Click rs-date-range-select div:has-text("Von") >> nth=3
    investigation.page.locator("text=VonBis >> #mat-input-0").fill("")
    # Press Enter
    investigation.page.locator("text=VonBis >> #mat-input-0").press("Enter")

    # Click .cell-content > .ng-star-inserted > .rs-tooltip-trigger > section >> nth=0
    with investigation.page.expect_popup() as popup:
        investigation.page.locator(".cell-content section:has-text('TestMeasure')  >> //ancestor::section"
                                   " >> //rs-status-icon//i[contains(@class, 'mail')] >> nth=1").click()
    popup = popup.value

    # Click text=Metadaten
    popup.locator("text=Metadaten").click()
    event_product = popup.locator("rs-attribute[label='Status']").first.inner_text()
    print(f"Event product: {event_product}")
    assert event_product == "-"

    # Click th[role="columnheader"]:has-text("IP")
    # popup.locator("th[role=\"columnheader\"]:has-text(\"IP\")")
    # Todo: Label Liste mit Json ersetzen
    labels = [
              "Start",
              "Ende",
              "Dauer",
              "Funkzellenstandort",
              "Richtung",
              "Verbindungsstatus",
              "Leistungsmerkmal",
              "Weiterleitungsziel",
              "Übertragungstechnik",
              "IMSI",
              "IMEI",
              "Gerät",
              "Anrufer",
              "Zeitstempel",
              "Angerufener"
              ]
    for label in labels:
        expected_locator = "unassigned"
        try:
            # locator = f"rs-attribute[label='{label}']"
            locator = f"rs-attribute[label='{label}']"
            expected_locator = str(expect(investigation.popup.locator(locator).first).to_be_visible())
            print(f"Label {locator} status visibility: '{expected_locator}'")
        except AttributeError:
            print(f"Label: {label} was not valid with {expected_locator}")
    # Make popup Object available for other tests
    investigation.popup = popup


@then(parsers.parse('the headline of the widget is "Kommunikationsdetails"'))
def check_fields(investigation, investigation_popup, helpers):
    investigation_popup.locator("text=Kommunikationsdetails").screenshot()
    # allure.attach(investigation_popup.locator(selector='div', has_text="Identitäten").first.screenshot())




