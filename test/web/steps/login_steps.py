from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from test.web.helpers.auth_state import ensure_user_auth_state
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


@when("I log out")
def log_out(page: Page):
    LoginPage(page).click_logout()


@when("I check the remember me checkbox")
def check_remember_me(page: Page):
    LoginPage(page).check_remember_me()


@then("the session cookie should persist")
def check_session_cookie_persists(page: Page):
    LoginPage(page).check_session_cookie_persists()


@then("I should be redirected to the login page")
def check_redirected_to_login(page: Page):
    LoginPage(page).check_on_signin_page()


@given(parsers.parse('the user "{username}" is logged in'), target_fixture="page")
def logged_in_page(browser, username: str):
    state_path = ensure_user_auth_state(browser, username)
    context = browser.new_context(storage_state=str(state_path))
    page = context.new_page()
    LoginPage(page).load()
    yield page
    context.close()
