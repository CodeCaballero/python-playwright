from config.settings import WEB_BASE_URL
from playwright.sync_api import expect

from test.web.pages.base_page import BasePage


class UserSettingsPage(BasePage):
    @property
    def _loc_first_name_input(self):
        return self.page.get_by_role("textbox", name="First Name")

    @property
    def _loc_email_input(self):
        return self.page.get_by_role("textbox", name="Email")

    @property
    def _loc_save_button(self):
        return self.page.get_by_test_id("user-settings-submit")

    @property
    def _loc_sidenav_full_name(self):
        return self.page.get_by_test_id("sidenav-user-full-name")

    def load(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/user/settings")

    def update_first_name(self, first_name: str):
        self._loc_first_name_input.fill(first_name)
        self._loc_save_button.click()

    def enter_email(self, email: str):
        self._loc_email_input.fill(email)

    def check_sidenav_full_name_contains(self, expected: str):
        expect(self._loc_sidenav_full_name).to_contain_text(expected)

    def check_validation_error(self, message: str):
        expect(self.page.get_by_text(message)).to_be_visible()

    def check_save_disabled(self):
        expect(self._loc_save_button).to_be_disabled()
