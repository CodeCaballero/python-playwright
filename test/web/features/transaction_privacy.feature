Feature: Transaction Privacy

  @reset_db
  Scenario: Only public transactions are visible to unrelated users
    Given a "public" payment of "5" from "Heath93" to "Judah_Dietrich50" with note "QA public visibility" already exists
    And a "private" payment of "5" from "Heath93" to "Judah_Dietrich50" with note "QA private visibility" already exists
    And A created user named "qa_stranger_e2e" with password "s3cret"
    And I am on the login page
    When I enter username "qa_stranger_e2e" and password "s3cret"
    And I click the login button
    And I go to the public transactions feed
    Then I should see the transaction "QA public visibility" in the feed
    And I should not see the transaction "QA private visibility" in the feed

  Scenario: A private transaction is visible to its own participants
    Given a "private" payment of "5" from "Heath93" to "Judah_Dietrich50" with note "QA private own visibility" already exists
    And the user "Heath93" is logged in
    And I am on the personal transactions page
    Then I should see the transaction "QA private own visibility" in the feed
