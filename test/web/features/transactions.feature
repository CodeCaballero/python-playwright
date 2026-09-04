Feature: Transaction Export

  Scenario: Export personal transactions to CSV
    Given the user "Heath93" is logged in
    And I am on the personal transactions page
    When I click the export button
    Then the downloaded CSV file "transactions.csv" should include the header "Date,Sender,Receiver,Amount,Description,Status"

  Scenario: Send a payment to a contact
    Given the user "Heath93" is logged in
    When I go to the new transaction page
    And I send a payment of "10" to "Lia Rosenbaum" with note "QA payment test"
    Then I should see the transaction confirmation "Paid $10.00 for QA payment test"

  Scenario: Create a payment request
    Given the user "Heath93" is logged in
    When I go to the new transaction page
    And I request a payment of "10" from "Lia Rosenbaum" with note "QA request test"
    Then I should see the transaction confirmation "Requested $10.00 for QA request test"

  Scenario: Accept a pending payment request
    Given a pending payment request of "15" from "Judah_Dietrich50" to "Heath93" with note "QA accept test"
    And the user "Heath93" is logged in
    When I open the created transaction
    And I accept the payment request
    Then the request action buttons should no longer be visible

  Scenario: Reject a pending payment request
    Given a pending payment request of "15" from "Judah_Dietrich50" to "Heath93" with note "QA reject test"
    And the user "Heath93" is logged in
    When I open the created transaction
    And I reject the payment request
    Then the request action buttons should no longer be visible

  Scenario: Add a comment to a transaction
    Given the user "Heath93" is logged in
    And a payment of "5" to "Judah_Dietrich50" with note "QA comment test" already exists
    When I open the created transaction
    And I add the comment "Thanks for this!"
    Then I should see the comment "Thanks for this!"

  Scenario: Like a transaction
    Given the user "Heath93" is logged in
    And a payment of "5" to "Judah_Dietrich50" with note "QA like test" already exists
    When I open the created transaction
    And I like the transaction
    Then the transaction like count should be 1

  Scenario: View transaction detail
    Given the user "Heath93" is logged in
    And a payment of "5" to "Judah_Dietrich50" with note "QA detail test" already exists
    When I open the created transaction
    Then I should see the transaction detail for "QA detail test"

  Scenario: View the public transactions feed
    Given the user "Heath93" is logged in
    When I go to the public transactions feed
    Then I should see transactions in the feed

  Scenario: View the friends transactions feed
    Given the user "Heath93" is logged in
    When I go to the friends transactions feed
    Then I should see transactions in the feed

  Scenario: Filter personal transactions by date range
    Given the user "Heath93" is logged in
    And I am on the personal transactions page
    When I filter transactions from the last 2 days
    Then the date filter should show the last 2 days

  Scenario: Search for a user in the new transaction screen
    Given the user "Heath93" is logged in
    When I go to the new transaction page
    And I search for the user "Ruthie Prosacco"
    Then I should see only "Ruthie Prosacco" in the search results

  Scenario: Searching for an unknown user shows no results
    Given the user "Heath93" is logged in
    When I go to the new transaction page
    And I search for the user "zzznoresultzzz"
    Then I should see no search results

  @flaky
  Scenario: Filter personal transactions by amount range
    Given the user "Heath93" is logged in
    And I am on the personal transactions page
    When I drag the amount range slider below the default maximum
    Then the amount filter should be narrowed
