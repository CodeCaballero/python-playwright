from playwright.sync_api import expect

from config.settings import WEB_BASE_URL
from test.web.pages.base_page import BasePage

class OnboardingPage(BasePage):

    @property
    def _loc_onboarding_title(self):
        return self.page.get_by_test_id('user-onboarding-dialog-title')

    def verify_onboarding_title(self):
        expect(self._loc_onboarding_title).to_be_visible()
        expect(self._loc_onboarding_title).to_have_text("Get Started with Real World App")
