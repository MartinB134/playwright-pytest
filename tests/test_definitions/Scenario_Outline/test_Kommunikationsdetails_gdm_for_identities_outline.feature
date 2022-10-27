Feature: [Phone]AdjustDdEA Widget Identitäten to new GDM fields, new Event API and name
        Dieser Test prüft ab:
          - ob alle Labels in der GUI übereinstimmen mit der Definition im generischen Datenmodell
  Scenario Outline: Check Identities GDM for multiple Event Types
    Given I opened a DdeA for a <communication_event>
    Then the following <attributes> out of the GDM are added / adjusted to the widget
    And the headline of the widget is "Kommunikationsdetails"
  Examples:
    | communication_event | attributes      |
    | phone call          | gdm_phone_call  |
    | sms                 | gdm_sms         |