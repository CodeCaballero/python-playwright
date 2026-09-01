from pathlib import Path

from config.paths import AUTH_DIR
from config.settings import API_BASE_URL
from config.users import get_password_user
from playwright.sync_api import Browser

from test.api.helpers.api_client import ApiClient
from test.web.pages.login_page import LoginPage


def ensure_user_auth_state(browser: Browser, username: str) -> str:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    state_path = AUTH_DIR / f"{username.lower()}.json"

    if state_path.exists() and not _is_state_valid(browser, state_path):
        state_path.unlink()

    if not state_path.exists():
        context = browser.new_context()
        page = context.new_page()
        login = LoginPage(page)
        login.load()
        login.do_login(username, get_password_user(username))
        login.click_login()
        login.check_username(username)
        context.storage_state(path=state_path)
        context.close()

    return str(state_path)


def _is_state_valid(browser: Browser, state_path: Path) -> bool:
    context = browser.new_context(storage_state=str(state_path))
    try:
        response = ApiClient(context.request, base_url=API_BASE_URL).get_transactions()
        return response.status == 200
    finally:
        context.close()
