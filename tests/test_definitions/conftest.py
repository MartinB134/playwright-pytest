# Copyright (c) Microsoft Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import json
import pytest
from pytest_html import extras
from pages.Amazon import Amazon
from pytest_bdd import parsers, given

TESTDATA_PATH = "tests/assets/testdata.json"
pytest.Amazon_URL = "https://www.amazon.com"

# The testdir fixture which we use to perform unit tests will set the home directory
# To a temporary directory of the created test. This would result that the browsers will
# be re-downloaded each time. By setting the pw browser path directory we can prevent that.
if sys.platform == "darwin":
    playwright_browser_path = os.path.expanduser("~/Library/Caches/ms-playwright")
elif sys.platform == "linux":
    playwright_browser_path = os.path.expanduser("~/.cache/ms-playwright")
elif sys.platform == "win32":
    user_profile = os.environ["USERPROFILE"]
    playwright_browser_path = f"{user_profile}\\AppData\\Local\\ms-playwright"
else:
    playwright_browser_path = f"No browser found"

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = playwright_browser_path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.assets.django.settings")

###############################################
# Share data for testing in scope feature
################################################
pytest.initial_testdata = "Starting point data. Not yet filled."


# Get contents of testdata.json to initial_testdata string

@pytest.fixture()
def write_testdata_to_current_page_class(amazon):
    file = open(os.path.abspath(TESTDATA_PATH), 'r')
    testdata_json = json.loads(file.read())
    pytest.initial_testdata = testdata_json
    amazon.testdata = testdata_json


@pytest.fixture()
def read_database():
    file = open(os.path.abspath(TESTDATA_PATH), 'r')
    testdata = json.loads(file.read())
    return testdata


@pytest.fixture()
def products(read_database):
    return read_database["products"]


@pytest.fixture(autouse=True)
def write_price_to_products(price="0", product="empty"):
    # Function only runs with passed in arguments
    if product == "empty":
        return pytest.initial_testdata
    test_data_new = pytest.initial_testdata
    new_data = Helpers.change_nested_json_values(test_data_new,
                                                 ["products", product, "product_price"],
                                                 price)
    print(f"Price '{price}' added to product '{product}'")


@pytest.fixture
def amazon(page):
    return Amazon(page)


@pytest.fixture
def helpers():
    """Make functions accessible that are not test specific with "helpers." notation

    :return: Helper functions
    :rtype:
    """
    return Helpers


###################
#       Hooks
###################
def pytest_bdd_before_scenario(request):
    pass


def pytest_bdd_after_step(request, step):
    print(f"Calling Step \n '{step}'")


def pytest_bdd_step_error(step, step_func, exception):
    print(f"=============== Custom Failure Report ============================/\n"
          f"Step: '{step.name}' failed in function: '{step_func}'\n"
          f"Exception: '{exception}'")


def pytest_bdd_after_scenario(request, feature, scenario):
    print(f"Close Page after scenario - to be implemented")
    # Amazon(page).page.close() # needed?


########################
#     Shared steps
# ######################
@given(parsers.parse("A browser is opened at page amazon"), target_fixture="page")
def return_amazon_page(page):
    page.goto(f"{pytest.Amazon_URL}")
    return page


@given(parsers.parse("Zipcode is set the US address {zipcode}"))
def change_zipcode_us(zipcode, amazon=return_amazon_page):
    # Click locator to change address
    amazon.page.wait_for_url(f"{pytest.Amazon_URL}*")
    # Anomaly where the amazon page starts at a different state
    if amazon.page.locator("a:has-text('Departments')").is_visible():
        # Reset Page
        amazon.page.locator("text=Departments").first.click()
    # Sometimes amazon starts at a different amazon home page
    if not amazon.page.locator('//*[contains(@id,"nav-pack")]').is_visible():
        amazon.page.goto(f"{pytest.Amazon_URL}")
    amazon.page.locator('//*[contains(@id,"nav-pack")]').click()
    amazon.page.locator("[aria-label=\"oder geben Sie eine US-Postleitzahl an\"]").click()
    # Fill [aria-label="oder geben Sie eine US-Postleitzahl an"]
    amazon.page.locator("[aria-label=\"oder geben Sie eine US-Postleitzahl an\"]").fill(zipcode)
    amazon.page.wait_for_timeout(100)
    # Click confirm button
    amazon.page.locator("div[id='GLUXSpecifyLocationDiv'] .a-button-input").click()
    # Click second confirm button
    amazon.page.locator(".a-popover-footer input").click()


####################
# Helper functions
####################
class Helpers:
    """
    Functions that are  globally accessible with "helpers." notation
    """
    def write_testdata_to_current_page_class(amazon):
        file = open(os.path.abspath(TESTDATA_PATH), 'r')
        testdata_json = json.loads(file.read())
        pytest.initial_testdata = testdata_json
        amazon.testdata = testdata_json


''' Replace every warning message you want to override
def override_nameerror_warningmessage():
    warnings.warn(NameError("This message will be displayed instead of 'NameError' as message)"))
'''


##################################
# HTML Report - Customization
###############################
# This will append an url to the html report
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])
    if report.when == "call":
        # always add url to report
        extra.append(pytest_html.extras.url(pytest.Amazon_URL))
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # only add additional html on failure
            extra.append(pytest_html.extras.html("<div>Additional HTML on Failure/Skip</div>"))
        report.extra = extra


def test_extra(extra):
    extra.append(extras.text("String added in conftest. "
                             "Will appear in HTML report in the last column as a Link with name 'text'"
                             "If not overwritten, like in this test."))
