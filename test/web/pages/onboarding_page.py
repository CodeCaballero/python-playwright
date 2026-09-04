from playwright.sync_api import expect

from test.web.pages.base_page import BasePage


class OnboardingPage(BasePage):
    @property
    def _loc_onboarding_title(self):
        return self.page.get_by_test_id("user-onboarding-dialog-title")

    @property
    def _loc_next_button(self):
        return self.page.get_by_test_id("user-onboarding-next")

    @property
    def _loc_finished_heading(self):
        return self.page.get_by_role("heading", name="Finished")

    def verify_onboarding_title(self):
        expect(self._loc_onboarding_title).to_be_visible()
        expect(self._loc_onboarding_title).to_have_text("Get Started with Real World App")

    def click_next(self):
        self._loc_next_button.click()

    def check_finished_step(self):
        expect(self._loc_finished_heading).to_be_visible()
