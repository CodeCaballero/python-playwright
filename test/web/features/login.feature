# language: en
Feature: User Login

  Background:
    Given I am on the login page

  Scenario: Successful login with valid credentials
    When I enter username "Reuben97" and password "s3cret"
    And I click the login button
    Then I should see the dashboard and the username "Reuben97"