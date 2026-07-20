from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page, Browser
from test.web.pages.login_page import LoginPage
from test.web.helpers.auth_state import ensure_user_auth_state

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

@given(parsers.parse('the user "{username}" is logged in'),target_fixture="page")
def logged_in_page(browser, username: str):
    state_path = ensure_user_auth_state(browser, username)
    context = browser.new_context(storage_state=str(state_path))
    page = context.new_page()
    LoginPage(page).load()
    yield page
    context.close()
