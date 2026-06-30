from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page
from test.web.pages.login_page import LoginPage

@given("I am on the login page")
def go_to_login(page: Page):
    LoginPage(page).load()

@when(parsers.parse('I enter username "{username}" and password "{password}"'))
def enter_credentials(page: Page, username: str, password: str):
    LoginPage(page).do_login(username, password)

@when("I click the login button")
def click_login(page: Page):
    LoginPage(page).click_login()

@then(parsers.parse('I should see the dashboard and the username "{username}"'))
def step_impl(page: Page, username: str):
    LoginPage(page).check_username(username)


@then(parsers.parse('I should see the login error "{message}"'))
def check_login_error(page: Page, message: str):
    LoginPage(page).check_login_error(message)

