from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from test.web.pages.signup_page import SignupPage


@given("I am on the signup page")
def go_to_signup(page: Page):
    SignupPage(page).load()


@when(
    parsers.parse(
        'I fill the sign up form with first name "{first_name}", last name "{last_name}", '
        'username "{username}", password "{password}" and confirm password '
        '"{confirm_password}"'
    )
)
def fill_signup_form(
    page: Page, first_name: str, last_name: str, username: str, password: str,
    confirm_password: str,
):
    SignupPage(page).fill_form(first_name, last_name, username, password, confirm_password)


@when("I click the sign up button")
def click_signup_submit(page: Page):
    SignupPage(page).click_submit()


@then("I should be redirected to the sign in page")
def check_redirected_to_signin(page: Page):
    SignupPage(page).check_redirected_to_signin()


@then(parsers.parse('I should see the sign up validation error "{message}"'))
def check_signup_validation_error(page: Page, message: str):
    signup_page = SignupPage(page)
    signup_page.check_validation_error(message)
    signup_page.check_submit_disabled()
