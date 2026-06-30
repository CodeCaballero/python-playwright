import pytest

from config.settings import API_BASE_URL
from test.api.login.login_client import LoginClient


@pytest.fixture
def login_client(playwright):
    base_url = API_BASE_URL
    api_context = playwright.request.new_context(base_url=base_url)
    yield LoginClient(api_context, base_url=base_url)
    api_context.dispose()