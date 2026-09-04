from playwright.sync_api import Page
from pytest_bdd import given, then, when

from test.web.pages.notifications_page import NotificationsPage


@given("I am on the notifications page")
def go_to_notifications(page: Page):
    NotificationsPage(page).load()


@then("I should see the list of notifications")
def check_notifications_list_visible(page: Page):
    NotificationsPage(page).check_notifications_list_visible()


@when("I dismiss the first notification", target_fixture="dismissed_notification_text")
def dismiss_first_notification(page: Page):
    return NotificationsPage(page).mark_first_notification_as_read()


@then("that notification should no longer be visible")
def check_dismissed_notification_hidden(page: Page, dismissed_notification_text: str):
    NotificationsPage(page).check_notification_not_visible(dismissed_notification_text)
