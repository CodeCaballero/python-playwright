import json
from pathlib import Path

import pytest
from config.settings import API_BASE_URL

from test.api.helpers.database_api import DatabaseApi
from test.builder.user_builder import UserBuilder

pytest_plugins = [
    "test.web.steps.login_steps",
    "test.web.steps.onboarding_steps",
    "test.web.steps.create_user_steps",
    "test.web.steps.transactions_steps",
    "test.web.steps.bank_accounts_steps",
    "test.web.steps.notifications_steps",
    "test.web.steps.user_settings_steps",
    "test.web.steps.signup_steps",
]


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


def pytest_bdd_apply_tag(tag, function):
    if tag == "flaky":
        # Deliberately not pytest-rerunfailures' own "flaky" marker: its mere presence
        # reruns the test (default 1 rerun) even with no reruns= kwarg, which would
        # mask a real bug behind a passing rerun. Instead: run once, don't fail the
        # build on it (xfail, strict=False so an unexpected pass doesn't fail either),
        # and tag it so pytest_sessionfinish below marks it "flaky" in the Allure report.
        pytest.mark.known_flaky(function)
        pytest.mark.xfail(
            reason="Known flaky scenario - does not block CI, tracked as flaky in Allure",
            strict=False,
        )(function)
        return True
    return None


def pytest_sessionfinish(session):
    alluredir = session.config.getoption("allure_report_dir", default=None)
    if not alluredir:
        return

    results_dir = Path(alluredir)
    if not results_dir.is_dir():
        return

    for result_file in results_dir.glob("*-result.json"):
        data = json.loads(result_file.read_text(encoding="utf-8"))
        labels = data.get("labels", [])
        is_known_flaky = any(
            label.get("name") == "tag" and label.get("value") == "known_flaky"
            for label in labels
        )
        if not is_known_flaky:
            continue

        data.setdefault("statusDetails", {})["flaky"] = True
        result_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
