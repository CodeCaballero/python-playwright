from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from test.web.pages.user_settings_page import UserSettingsPage


@given("I am on the user settings page")
def go_to_user_settings(page: Page):
    UserSettingsPage(page).load()


@when(parsers.parse('I update the first name to "{first_name}"'))
def update_first_name(page: Page, first_name: str):
    UserSettingsPage(page).update_first_name(first_name)


@then(parsers.parse('I should see "{expected}" reflected in the sidenav'))
def check_sidenav_full_name(page: Page, expected: str):
    UserSettingsPage(page).check_sidenav_full_name_contains(expected)


@when(parsers.parse('I enter the email "{email}"'))
def enter_email(page: Page, email: str):
    UserSettingsPage(page).enter_email(email)


@then(parsers.parse('I should see the settings validation error "{message}"'))
def check_settings_validation_error(page: Page, message: str):
    user_settings_page = UserSettingsPage(page)
    user_settings_page.check_validation_error(message)
    user_settings_page.check_save_disabled()
