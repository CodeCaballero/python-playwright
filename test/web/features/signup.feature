Feature: Sign Up

  @reset_db
  Scenario: Sign up successfully and log in with the new account
    Given I am on the signup page
    When I fill the sign up form with first name "QA", last name "SignupFlow", username "qa_e2e_signup", password "s3cret123" and confirm password "s3cret123"
    And I click the sign up button
    Then I should be redirected to the sign in page
    When I enter username "qa_e2e_signup" and password "s3cret123"
    And I click the login button
    Then I should see the dashboard and the username "qa_e2e_signup"

  Scenario: See a validation error when passwords do not match
    Given I am on the signup page
    When I fill the sign up form with first name "QA", last name "Mismatch", username "qa_e2e_mismatch", password "s3cret123" and confirm password "different"
    Then I should see the sign up validation error "Password does not match"
