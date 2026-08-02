from playwright.sync_api import Page
from pytest_bdd import then

from test.web.pages.onboarding_page import OnboardingPage


@then("the onboarding dialog title is shown")
def the_onboarding_dialog_title_is_shown(page: Page):
    OnboardingPage(page).verify_onboarding_title()
