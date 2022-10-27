Feature: [Phone]AdjustDdEA Widget Identitäten to new GDM fields, new Event API and name
        Dieser Test prüft ab:
          - ob alle Labels in der GUI übereinstimmen mit der Definition im generischen Datenmodell
  Scenario: Check Identities GDM for Phone Calls
    Given I opened a DdeA for a phone call communication event
    Then the following attributes out of the GDM are added / adjusted to the widget
    And the headline of the widget is "Kommunikationsdetails"
    # And Zipcode is set the US address 22161
    # And I find and add the cheapest product to the basket
    # When all products are added to the basket
    # Then Products are displayed with added sums in basket
    # Then Going to checkout leads to login