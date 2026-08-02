from test.builder.user_builder import UserBuilder

pytest_plugins = [
    "test.web.steps.login_steps",
    "test.web.steps.onboarding_steps",
    "test.web.steps.create_user_steps",
]

import pytest

from config.settings import API_BASE_URL
from test.api.helpers.database_api import DatabaseApi


@pytest.fixture
def database_api():
    return DatabaseApi(API_BASE_URL)


@pytest.fixture(autouse=True)
def reset_db_after_test(request):
    marker = request.node.get_closest_marker("reset_db")
    database_api = None
    if marker:
        database_api = request.getfixturevalue("database_api")
    yield
    if database_api is not None:
        database_api.reset_db()


@pytest.fixture
def create_user_with_builder(database_api):
    def _create_user(builder: UserBuilder):
        user_data = builder.build()
        database_api.create_user(user_data)
        return user_data

    return _create_user


@pytest.fixture(scope="session", autouse=True)
def configure_playwright_test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")

@pytest.fixture
def pytest_bdd_apply_tag(tag, function):
    if tag == "flaky":
        marker = pytest.mark.flaky(reruns=2, reruns_delay=1)
        marker(function)
        return True
    return None