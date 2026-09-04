from config.settings import WEB_BASE_URL
from playwright.sync_api import expect

from test.web.pages.base_page import BasePage


class SignupPage(BasePage):
    @property
    def _loc_first_name_input(self):
        return self.page.get_by_role("textbox", name="First Name")

    @property
    def _loc_last_name_input(self):
        return self.page.get_by_role("textbox", name="Last Name")

    @property
    def _loc_username_input(self):
        return self.page.get_by_role("textbox", name="Username")

    @property
    def _loc_password_input(self):
        return self.page.get_by_role("textbox", name="Password", exact=True)

    @property
    def _loc_confirm_password_input(self):
        return self.page.get_by_role("textbox", name="Confirm Password")

    @property
    def _loc_submit_button(self):
        return self.page.get_by_test_id("signup-submit")

    @property
    def _loc_signin_heading(self):
        return self.page.get_by_role("heading", name="Sign in")

    def load(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/signup")

    def fill_form(
        self, first_name: str, last_name: str, username: str, password: str, confirm_password: str
    ):
        self._loc_first_name_input.fill(first_name)
        self._loc_last_name_input.fill(last_name)
        self._loc_username_input.fill(username)
        self._loc_password_input.fill(password)
        self._loc_confirm_password_input.fill(confirm_password)

    def click_submit(self):
        self._loc_submit_button.click()

    def check_redirected_to_signin(self):
        expect(self._loc_signin_heading).to_be_visible()

    def check_validation_error(self, message: str):
        expect(self.page.get_by_text(message)).to_be_visible()

    def check_submit_disabled(self):
        expect(self._loc_submit_button).to_be_disabled()
