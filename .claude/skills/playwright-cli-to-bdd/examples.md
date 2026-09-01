# Diff → Framework Examples

Examples 1-3 show converting an already-captured Playwright/codegen snippet into
BDD (useful when a human pasted one in, e.g. from the manual `playwright codegen`
fallback). Example 4 shows the default flow: reading `app/diff.txt` directly and
drafting the code without ever running codegen.

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
    page.locator('[data-test="sidenav-username"]').click()
    expect(page.locator('[data-test="sidenav-username"]')).to_contain_text("Reuben97")
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

---

## Example 4 — Diff-driven, both paths (backend + frontend)

### Input (`app/diff.txt`, abridged)

```diff
diff --git a/backend/transaction-routes.ts b/backend/transaction-routes.ts
+//GET /transactions/export - scoped user, auth-required
+router.get(
+  "/export",
+  ensureAuthenticated,
+  validateMiddleware([...]),
+  (req, res) => {
+    const transactions = getTransactionsForUserForApi(req.user?.id!, req.query);
+    const csv = transactionsToCsv(transactions);
+    res.set("Content-Type", "text/csv");
+    res.send(csv);
+  }
+);

diff --git a/src/components/TransactionListFilters.tsx b/src/components/TransactionListFilters.tsx
+        {onExport && (
+          <Grid item sx={{ marginLeft: "auto" }}>
+            <Button
+              variant="contained"
+              color="primary"
+              data-test="transaction-list-export-button"
+              onClick={onExport}
+            >
+              Export CSV
+            </Button>
+          </Grid>
+        )}
```

### Step 1 — Classify

- New endpoint `GET /transactions/export`, auth-required, returns `text/csv` → **API path**.
- New button `data-test="transaction-list-export-button"` on the personal transactions filters, wired to call that endpoint → **Web path**.
- Both paths needed: one API test for the endpoint contract, one BDD scenario for the UI flow that triggers it.

### Step 4 — Reuse check

- `test/api/helpers/api_client.py` has `get_transactions()` but nothing for `/export` → new method needed.
- `test/api/transaction/test_transactions.py` already exists → add the test there, no new file.
- `test/web/steps/login_steps.py` already covers login → reuse as `Background` for the web scenario.
- No existing page object touches the transactions filters → new `TransactionsPage`.

### Output — `ApiClient` (add method)

```python
def get_transactions_export(self, params: dict | None = None):
    return self.request.get(f"{self.base_url}/transactions/export", params=params)
```

### Output — `test/api/transaction/test_transactions.py` (add test)

```python
def test_transactions_export(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_transactions_export()

    assert response.status == 200
    assert response.headers["content-type"].startswith("text/csv")
```

### Output — `test/web/pages/transactions_page.py` (new)

```python
from playwright.sync_api import expect

from test.web.pages.base_page import BasePage


class TransactionsPage(BasePage):
    @property
    def _loc_export_button(self):
        return self.page.get_by_test_id("transaction-list-export-button")

    def click_export(self):
        with self.page.expect_download() as download_info:
            self._loc_export_button.click()
        return download_info.value

    @staticmethod
    def assert_csv_downloaded(download):
        assert download.suggested_filename == "transactions.csv"
```

### Output — `test/web/steps/transactions_steps.py` (new)

```python
from playwright.sync_api import Page
from pytest_bdd import then, when

from test.web.pages.transactions_page import TransactionsPage


@when("I click the export button", target_fixture="download")
def click_export(page: Page):
    return TransactionsPage(page).click_export()


@then("a CSV file is downloaded")
def assert_csv_downloaded(download):
    TransactionsPage.assert_csv_downloaded(download)
```

`target_fixture` is the established way to pass state between steps in this framework — `login_steps.py` uses the same pattern for `"the user is logged in"`.

### Output — `test/web/features/transactions.feature` (new)

```gherkin
# language: en
Feature: Transactions Export

  Background:
    Given I am on the login page
    When I enter username "Heath93" and password "s3cret"
    And I click the login button

  Scenario: Export personal transactions as CSV
    When I click the export button
    Then a CSV file is downloaded
```

### Wire-up

```python
# test/web/test_scenarios.py
scenarios("transactions.feature")

# test/conftest.py
pytest_plugins = [
    "test.web.steps.login_steps",
    "test.web.steps.transactions_steps",
]
```

### Step 9 — Validate

```bash
uv run pytest test/api/transaction/test_transactions.py -v
uv run pytest test/web/ -k "Export personal transactions" -v --tracing=retain-on-failure
```

Both need to actually pass against the running app before this is considered done — a diff read correctly still needs the real endpoint/DOM to confirm it.
