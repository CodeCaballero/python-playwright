Feature: Bank Accounts

  Scenario: Add a bank account successfully
    Given the user "Heath93" is logged in
    And I am on the bank accounts page
    When I click create bank account
    And I fill the bank account form with bank name "QA New Bank", routing number "123456789" and account number "987654321"
    And I save the bank account
    Then I should see the bank account "QA New Bank" in the list

  Scenario: Delete a bank account
    Given the user "Heath93" is logged in
    And I am on the bank accounts page
    When I click create bank account
    And I fill the bank account form with bank name "QA Delete Bank", routing number "123456789" and account number "987654321"
    And I save the bank account
    And I delete the bank account "QA Delete Bank"
    Then the bank account "QA Delete Bank" should be marked as deleted

  Scenario: See a validation error for a missing routing number
    Given the user "Heath93" is logged in
    And I am on the bank accounts page
    When I click create bank account
    And I fill the bank account form with bank name "QA Bank" and account number "987654321", leaving the routing number blank
    Then I should see the bank account validation error "Enter a valid bank routing number"

  Scenario: See a validation error for a missing account number
    Given the user "Heath93" is logged in
    And I am on the bank accounts page
    When I click create bank account
    And I fill the bank account form with bank name "QA Bank" and routing number "123456789", leaving the account number blank
    Then I should see the bank account validation error "Enter a valid bank account number"
