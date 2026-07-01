# language: en
Feature: User Login

  Background:
    Given I am on the login page

  Scenario: Successful login with valid credentials
    When I enter username "Heath93" and password "s3cret"
    And I click the login button
    Then I should see the dashboard and the username "Heath93"

  Scenario: Failed login with invalid credentials
    When I enter username "test222" and password "2222222"
    And I click the login button
    Then I should see the login error "Username or password is invalid"