Feature: Notifications

  Scenario: View the list of notifications
    Given the user "Heath93" is logged in
    And I am on the notifications page
    Then I should see the list of notifications

  Scenario: Mark a notification as read
    Given the user "Heath93" is logged in
    And I am on the notifications page
    When I dismiss the first notification
    Then that notification should no longer be visible
