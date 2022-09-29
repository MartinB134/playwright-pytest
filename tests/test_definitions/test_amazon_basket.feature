Feature: Checking basic features of Amazon
  As a new Amazon user,
  I want to search for the cheapest Snickers and Skittles on the page
  and  add the cheapest ones to your Basket.
  - check if the basket calculates the result correctly.
  - check if the user gets redirected to the registration page
    - for the conditions: 1. using the checkout button
                          2. without an account registered
  Scenario: Check the amazon basket for multiple products
    Given A browser is opened at page amazon
    And Zipcode is set the US address 22161
    And I find and add the cheapest product to the basket
    When all products are added to the basket
    Then Products are displayed with added sums in basket
    Then Going to checkout leads to login