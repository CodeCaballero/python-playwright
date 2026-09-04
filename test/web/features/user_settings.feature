Feature: User Settings

  @reset_db
  Scenario: Update the user profile name
    Given the user "Heath93" is logged in
    And I am on the user settings page
    When I update the first name to "TedQA"
    Then I should see "TedQA" reflected in the sidenav

  Scenario: See a validation error for an invalid email
    Given the user "Heath93" is logged in
    And I am on the user settings page
    When I enter the email "not-an-email"
    Then I should see the settings validation error "Must contain a valid email address"
