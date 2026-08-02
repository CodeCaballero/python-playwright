Feature: User Login

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter username "Heath93" and password "s3cret"
    And I click the login button
    Then I should see the dashboard and the username "Heath93"

  Scenario: Failed login with invalid credentials
    Given I am on the login page
    When I enter username "test222" and password "2222222"
    And I click the login button
    Then I should see the login error "Username or password is invalid"

  Scenario: Login storage state
    Given the user "Heath93" is logged in
    Then I should see the dashboard and the username "Heath93"

  @flaky
  @reset_db
  Scenario Outline: Show onboarding with new user
    Given A created user named "<userName>" with password "<password>"
    Given I am on the login page
    When I enter username "<userName>" and password "<password>"
    And I click the login button
    Then the onboarding dialog title is shown
    Examples:
      | userName | password |
      | new_user | s3cret   |
