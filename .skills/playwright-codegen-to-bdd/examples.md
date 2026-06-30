# Codegen → BDD Examples

## Example 1 — Login (reuse existing steps)

### Input (codegen)

```python
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:3000/")
    page.get_by_role("textbox", name="Username").fill("Reuben97")
    page.get_by_role("textbox", name="Password").fill("s3cret")
    page.locator("button[type='submit']").click()
    page.locator("[data-test=\"sidenav-username\"]").click()
    expect(page.locator("[data-test=\"sidenav-username\"]")).to_contain_text("Reuben97")
    context.close()
    browser.close()
```

### Output — feature (already exists, reuse as-is)

```gherkin
Scenario: Successful login with valid credentials
  When I enter username "Reuben97" and password "s3cret"
  And I click the login button
  Then I should see the dashboard and the username "Reuben97"
```

**Reuse:** all three steps already in `login_steps.py`. **No new files needed** — only a new Scenario block if testing different data.

---

## Example 2 — New flow (bank account navigation)

### Input (codegen)

```python
page.goto("http://localhost:3000/")
page.get_by_role("textbox", name="Username").fill("Reuben97")
page.get_by_role("textbox", name="Password").fill("s3cret")
page.locator("button[type='submit']").click()
page.get_by_role("link", name="Bank Accounts").click()
expect(page.get_by_role("heading", name="Bank Accounts")).to_be_visible()
```

### Step reuse analysis

| Codegen action | Existing step? | Action |
|----------------|----------------|--------|
| goto + fill + click login | Yes — login steps | Reuse in Background |
| click Bank Accounts link | No | New step + page method |
| expect heading visible | No | New Then step + assertion |

### Output — feature

```gherkin
# language: en
Feature: Bank Accounts

  Background:
    Given I am on the login page
    When I enter username "Reuben97" and password "s3cret"
    And I click the login button

  Scenario: View bank accounts list
    When I open the bank accounts page
    Then I should see the bank accounts heading
```

### Output — page (`test/web/pages/bank_accounts_page.py`)

```python
from playwright.sync_api import expect

from test.web.pages.base_page import BasePage


class BankAccountsPage(BasePage):

    @property
    def _loc_nav_bank_accounts(self):
        return self.page.get_by_role("link", name="Bank Accounts")

    @property
    def _loc_heading(self):
        return self.page.get_by_role("heading", name="Bank Accounts")

    def open_from_sidebar(self):
        self._loc_nav_bank_accounts.click()

    def assert_heading_visible(self):
        expect(self._loc_heading).to_be_visible()
```

### Output — steps (`test/web/steps/bank_accounts_steps.py`)

```python
from pytest_bdd import when, then
from playwright.sync_api import Page
from test.web.pages.bank_accounts_page import BankAccountsPage


@when("I open the bank accounts page")
def open_bank_accounts(page: Page):
    BankAccountsPage(page).open_from_sidebar()


@then("I should see the bank accounts heading")
def assert_bank_accounts_heading(page: Page):
    BankAccountsPage(page).assert_heading_visible()
```

### Wire-up

```python
# test/web/test_scenarios.py
scenarios("bank_accounts.feature")

# test/conftest.py
pytest_plugins = [
    "test.web.steps.login_steps",
    "test.web.steps.bank_accounts_steps",
]
```

---

## Example 3 — Locator upgrade from weak codegen

Codegen often produces brittle selectors. Upgrade while converting:

| Codegen (weak) | Framework (strong) |
|----------------|-------------------|
| `page.locator("#root > div > button")` | `page.get_by_role("button", name="Sign in")` |
| `page.locator(".MuiButton-root")` | `page.get_by_role("button", name="...")` |
| `page.locator("input:nth-child(2)")` | `page.get_by_role("textbox", name="Password")` |
| `page.locator("[data-test=foo]")` | Keep — `page.locator('[data-test="foo"]')` |

Always re-check codegen locators against accessible roles before committing to `_loc_*` properties.
