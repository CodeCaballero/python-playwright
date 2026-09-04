from playwright.sync_api import Page
from pytest_bdd import then, when

from test.web.pages.onboarding_page import OnboardingPage


@then("the onboarding dialog title is shown")
def the_onboarding_dialog_title_is_shown(page: Page):
    OnboardingPage(page).verify_onboarding_title()


@when("I click next on the onboarding dialog")
def click_next_on_onboarding(page: Page):
    OnboardingPage(page).click_next()


@then("the onboarding finished step is shown")
def the_onboarding_finished_step_is_shown(page: Page):
    OnboardingPage(page).check_finished_step()
