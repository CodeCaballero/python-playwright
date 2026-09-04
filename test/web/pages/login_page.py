from config.settings import WEB_BASE_URL
from playwright.sync_api import expect

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
        return self.page.get_by_test_id("signin-submit")

    @property
    def _loc_signin_error(self):
        return self.page.get_by_test_id("signin-error")

    @property
    def _loc_sidenav_username(self):
        return self.page.get_by_test_id("sidenav-username")

    @property
    def _loc_logout_button(self):
        return self.page.get_by_test_id("sidenav-signout")

    @property
    def _loc_signin_heading(self):
        return self.page.get_by_role("heading", name="Sign in")

    @property
    def _loc_remember_me_checkbox(self):
        return self.page.get_by_role("checkbox", name="Remember me")

    def load(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/signin")

    def do_login(self, username: str, password: str):
        self._loc_input_username.fill(username)
        self._loc_input_password.fill(password)

    def check_remember_me(self):
        self._loc_remember_me_checkbox.check()

    def click_login(self):
        self._loc_button_login.click()

    def click_logout(self):
        self._loc_logout_button.click()

    def check_username(self, username: str):
        expect(self._loc_sidenav_username).to_contain_text(username)

    def check_login_error(self, message: str):
        expect(self._loc_signin_error).to_contain_text(message)

    def check_on_signin_page(self):
        expect(self._loc_signin_heading).to_be_visible()

    def check_session_cookie_persists(self):
        cookies = self.page.context.cookies()
        session_cookie = next(cookie for cookie in cookies if cookie["name"] == "connect.sid")
        assert session_cookie["expires"] > 0, (
            "Expected the session cookie to persist (Remember me), got a session-only cookie"
        )
