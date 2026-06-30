from playwright.sync_api import expect

from config.settings import WEB_BASE_URL
from test.web.pages.base_page import BasePage


class LoginPage(BasePage):

    @property
    def _loc_input_username(self):
        return self.page.get_by_role("textbox", name="Username")

    @property
    def _loc_input_password(self):
        return self.page.get_by_role("textbox", name="Password")

    @property
    def _loc_button_login(self):
        return self.page.locator("[data-test=\"signin-submit\"]")

    @property
    def _loc_signin_error(self):
        return self.page.locator("[data-test=\"signin-error\"]")

    @property
    def _loc_sidenav_username(self):
        return self.page.locator("[data-test=\"sidenav-username\"]")

    def load(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/signin")

    def do_login(self, username: str, password: str):
        self._loc_input_username.fill(username)
        self._loc_input_password.fill(password)

    def click_login(self):
        self._loc_button_login.click()

    def check_username(self, username: str):
        expect(self._loc_sidenav_username).to_contain_text(username)

    def check_login_error(self, message: str):
        expect(self._loc_signin_error).to_contain_text(message)