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

  Scenario: Log out ends the session
    Given I am on the login page
    When I enter username "Heath93" and password "s3cret"
    And I click the login button
    And I log out
    Then I should be redirected to the login page
    When I am on the personal transactions page
    Then I should be redirected to the login page

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

  Scenario: Remember me keeps a persistent session cookie
    Given I am on the login page
    When I enter username "Heath93" and password "s3cret"
    And I check the remember me checkbox
    And I click the login button
    Then I should see the dashboard and the username "Heath93"
    And the session cookie should persist

  @reset_db
  Scenario: Complete onboarding by creating the first bank account
    Given A created user named "qa_onboard_complete" with password "s3cret"
    Given I am on the login page
    When I enter username "qa_onboard_complete" and password "s3cret"
    And I click the login button
    Then the onboarding dialog title is shown
    When I click next on the onboarding dialog
    And I fill the bank account form with bank name "QA Onboard Bank", routing number "123456789" and account number "987654321"
    And I save the bank account
    Then the onboarding finished step is shown
    When I click next on the onboarding dialog
    And I am on the bank accounts page
    Then I should see the bank account "QA Onboard Bank" in the list
