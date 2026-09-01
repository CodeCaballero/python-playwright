---
name: playwright-cli-to-bdd
description: >
  Reads a PR diff (default app/diff.txt) to detect new/changed backend routes
  and UI features, then drives Playwright itself — headless, scripted, no
  recording — against the running app to confirm the real selectors/DOM/
  response shape before writing anything. Converts the confirmed interaction
  into framework-conformant tests: pytest-bdd (features, steps, page objects)
  for frontend changes, plain pytest + ApiClient for backend-only changes.
  Validates the result by running the real test suite with Playwright CLI
  (pytest-playwright) against the running app. Every touchpoint with
  Playwright is CLI/script-driven and agent-run — never interactive codegen,
  never a human recording clicks. Reuses existing steps/page objects/
  ApiClient methods whenever possible. Use when a PR diff introduces backend
  or frontend changes and you need to generate test coverage for them.
---

# Diff → QA Framework (BDD + API)

**Input source:** a PR diff file, default `app/diff.txt` (git diff of the app under test — see `README.md` for how it's cloned into `app/`). The diff tells you **what** changed and roughly **where** — it is never trusted as the final source of truth for a selector.

**Two automated touchpoints with Playwright, both agent-driven, neither is `codegen`:**

1. **Live verification (Step 3)** — a throwaway headless script, written by the agent and run with `uv run python <script>.py`, that opens the real running app and proves each candidate locator resolves to exactly one element (or, for the API side, that the real endpoint returns the expected shape). This replaces guessing a selector from JSX in the diff — the diff gives you the lead (`data-test="x"`, a button's visible text, a route path), the live script gives you the proof.
2. **Final validation (Step 9)** — running the generated framework tests for real with `uv run pytest ...` (Playwright CLI under `pytest-playwright`) against the same running app.

`playwright codegen` / `playwright open` are **not used anywhere in this skill** — they require a human clicking through the app, and every step here must be runnable unattended by the agent.

**Goal:** generate tests that follow the existing layered architecture and conventions — never paste raw Playwright/request code directly into steps, features, or test files.

## Usage

This skill lives at `.claude/skills/playwright-cli-to-bdd/SKILL.md` — that's the path Claude Code auto-discovers project skills from (`.skills/` at the repo root, without `.claude/`, is **not** scanned and will show as an unknown command).

```
/playwright-cli-to-bdd
```

That's the whole invocation — Step 3 (live verification script) and Step 9 (`pytest` validation) run automatically as part of the workflow below, no separate Playwright CLI call needed from you.

Diff path defaults to `app/diff.txt`. To point at a different one, pass it as the argument — it arrives as `$ARGUMENTS`, use that path instead of the default in Step 1:

```
/playwright-cli-to-bdd path/to/other-diff.txt
```

**Before invoking:** the app must be running at `WEB_BASE_URL` / `API_BASE_URL` (`cd app && yarn dev`, per `README.md`) — Step 2 checks this, but Steps 3 and 9 can't do anything useful if it's down. Make sure `app/diff.txt` (or your custom path) reflects the PR/branch you want covered — regenerate it yourself first if it's stale, e.g. `git -C app diff main... > app/diff.txt`.

---

## Scope: which path does the diff need?

Classify each diff before generating anything:

| Diff touches... | Path |
|---|---|
| `backend/**` (routes, validators) only | **API path** — plain pytest + `ApiClient` |
| `src/**` UI components/containers only | **Web path** — pytest-bdd (feature/steps/page) |
| Both (e.g. new backend route wired to a new UI action) | **Both paths** — one API test for the endpoint, one BDD scenario for the UI flow that calls it |

If the diff contains no testable backend or frontend change (styling only, refactor with no behavior change, types, tests, CI config), say so and generate nothing.

## Architecture

```
test/web/
├── features/<domain>.feature      # Gherkin scenarios
├── steps/<domain>_steps.py        # @given / @when / @then (thin — call Page Objects)
├── pages/<domain>_page.py         # Locators (@property _loc_*) + actions + assertions
└── test_scenarios.py              # scenarios("<domain>.feature") — add new features here
test/api/
├── helpers/api_client.py          # One method per endpoint (post_x, get_x) — extend, don't bypass
└── <domain>/test_<domain>.py      # Plain pytest, parametrized where it fits (see test_login.py)
test/conftest.py                   # pytest_plugins — register new *_steps.py modules
test/api/conftest.py               # api_client / api_client_with_auth fixtures
config/settings.py                 # WEB_BASE_URL / API_BASE_URL — never hardcode URLs or ports
```

## Workflow

Copy this checklist and track progress — each item maps 1:1 to a section below:

```
[ ] 1.  Read the diff → classify path (API / Web / Both) and list what changed
[ ] 2.  Check prerequisites — is the app running at WEB_BASE_URL / API_BASE_URL?
[ ] 3.  Verify live — script the candidate selectors/endpoint against the running app
[ ] 4.  Inventory existing steps/pages (web) or ApiClient methods (api) — reuse first
[ ] 5.  Decide: extend an existing Page Object/ApiClient vs create a new one
[ ] 6.  Implement — locators/actions (web) or client methods (api), using only what Step 3 confirmed
[ ] 7.  Write the Gherkin feature (web) or the pytest test function (api)
[ ] 8.  Wire up — test_scenarios.py + conftest.py pytest_plugins (web only)
[ ] 9.  Validate — run the new test(s) with Playwright CLI against the live app
[ ] 10. Verify names, imports, and conventions before finishing
```

### Step 1 — Read and classify the diff

- New routes/endpoints (`router.get(...)`, `router.post(...)`) and their auth/validation.
- New UI elements (buttons, fields, tables, messages) and their `data-test` / accessible name.
- Text changes (labels, placeholders, titles, error messages).
- New flows connecting the two (a button that calls a new endpoint).
- Note what needs to be tested and in what order. If nothing is testable, stop and say so.

### Step 2 — Check prerequisites

Before drafting anything that will need validation, confirm the app is reachable:

```bash
curl -sf $WEB_BASE_URL >/dev/null && echo "web up" || echo "web down"
curl -sf $API_BASE_URL >/dev/null && echo "api up" || echo "api down"
```

If it's down, tell the user to start it per `README.md` (`cd app && yarn dev`) before Step 9 — you can still draft the code without it running, but you cannot validate.

### Step 3 — Verify live: script it, don't guess it

The diff gives you a *lead*, never a confirmed locator. Turn each lead into a candidate, then prove it against the running app with a small headless script — no interactive tool, no recording, just the Playwright API called from a normal Python file you write and run yourself.

**Web — confirm the candidate locator resolves to exactly one element, on the real page, in its real state (e.g. logged in):**

```python
# scratch verification script — not committed, delete when done
from playwright.sync_api import sync_playwright
from config.settings import WEB_BASE_URL

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_context(storage_state=".auth/heath93.json").new_page()
    page.goto(f"{WEB_BASE_URL}/personal")

    candidate = page.get_by_test_id("transaction-list-export-button")
    print("count:", candidate.count())          # must be 1
    print("visible:", candidate.is_visible())
    print("text:", candidate.inner_text())

    browser.close()
```

Run it with `uv run python <script>.py` (Step 2 must have confirmed the app is up first). Reuse an existing `.auth/*.json` from `test/web/helpers/auth_state.py` for logged-in state instead of logging in manually in the script. If `count()` isn't 1, or the diff's `data-test` doesn't actually appear at runtime (conditional rendering, a wrapper component, a typo), inspect `page.content()` or narrow with `page.get_by_role(...)` until you find the real one — never fall back to a guessed CSS selector.

**API — confirm the real endpoint, status code, and response shape** (a request script, or `curl`, both count as "scripted" — pick whichever is faster):

```bash
curl -s -i -b "session=<cookie-from-a-logged-in-run>" "$API_BASE_URL/transactions/export"
```

or, staying inside the framework's own client for a closer approximation:

```python
from playwright.sync_api import sync_playwright
from config.settings import API_BASE_URL

with sync_playwright() as p:
    ctx = p.request.new_context(base_url=API_BASE_URL)
    ctx.post("/login", data={"username": "Heath93", "password": "s3cret"})
    r = ctx.get("/transactions/export")
    print(r.status, dict(r.headers))
    ctx.dispose()
```

Only once Step 3 has actually printed a confirmed count/status/shape do you move on — Step 6 implements exactly what was confirmed here, nothing inferred beyond it.

If the app isn't running (Step 2 was "down"), you cannot complete this step — say so and stop; don't draft code against an unverified guess.

### Step 4 — Reuse existing code (mandatory before writing anything new)

**Web:** read every file in `test/web/steps/` and the related `.feature` files for phrasing already in use.
**API:** read `test/api/helpers/api_client.py` and the existing `test/api/**/test_*.py` for methods/fixtures already in use.

Reuse rules:
- Same user action + same meaning → reuse the exact step text (e.g., `I click the login button`).
- Same action, different target → parametrize with `parsers.parse` and `{name}` placeholders.
- Same endpoint, different inputs → add a case to an existing `@pytest.mark.parametrize` table (see `test_login.py`) instead of a new test function.
- Only create new steps/methods/tests when nothing existing covers the intent.

Anti-pattern: paraphrasing an existing step or duplicating an `ApiClient` method under a new name.

### Step 5 — Extend vs. create

- **Web:** extend the current Page Object when the flow stays on the same screen/domain; create `test/web/pages/<new>_page.py` when navigating to a new area.
- **API:** add a method to `ApiClient` for any new endpoint, regardless of domain — it's a flat client, not per-domain. Put the test itself in `test/api/<domain>/test_<domain>.py`, creating the domain folder only if genuinely new.

### Step 6 — Implement

Use only what Step 3 actually confirmed — the script's printed `count`/`status`/shape, not what the diff seemed to imply.

**Web page object:**

```python
from playwright.sync_api import expect

from config.settings import WEB_BASE_URL
from test.web.pages.base_page import BasePage


class ExamplePage(BasePage):
    @property
    def _loc_submit(self):
        return self.page.get_by_role("button", name="Submit")

    def load(self):
        self.navigate_to(WEB_BASE_URL)  # or path: f"{WEB_BASE_URL}/settings"

    def click_submit(self):
        self._loc_submit.click()

    def assert_success_message(self, text: str):
        expect(self.page.get_by_text(text)).to_be_visible()
```

Locator rules:
- Private properties: `_loc_<element_purpose>` as `@property` returning a Locator.
- Prefer `get_by_role` > `get_by_label` > `get_by_test_id` > CSS (CSS is a last resort, never a first draft).
- Assertions use `expect(...)` inside page methods, not in steps.
- Inherit `BasePage`; use `self.page`, `self.navigate_to()`.

**API client method** — add to `ApiClient`, one method per endpoint, no branching logic inside it:

```python
def get_transactions_export(self, params: dict | None = None):
    return self.request.get(f"{self.base_url}/transactions/export", params=params)
```

### Step 7 — Write the test

**Web — Gherkin:**

```gherkin
# language: en
Feature: <Human-readable domain name>

  Background:
    Given I am on the login page

  Scenario: <Outcome-oriented name>
    When I enter username "Reuben97" and password "s3cret"
    And I click the login button
    Then I should see the dashboard and the username "Reuben97"
```

- **Background** for shared preconditions — reuse `Given` steps from other features.
- Scenario names describe the **business outcome**, not the clicks.
- Quotes for string parameters matching `parsers.parse` placeholders.

**Web — steps (thin layer, calls the Page Object only):**

```python
@when("I click the export button")
def click_export(page: Page):
    TransactionsPage(page).click_export()
```

**API — plain pytest**, matching `test_login.py`'s style (parametrize when testing multiple input/status combinations, plain assertions with a message otherwise — see `test_transactions.py`):

```python
def test_transactions_export(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_transactions_export()

    assert response.status == 200
    assert response.headers["content-type"].startswith("text/csv")
```

### Step 8 — Wire up (web only)

**`test/web/test_scenarios.py`** — add one line per feature file:

```python
from pytest_bdd import scenarios

scenarios("login.feature")
scenarios("transactions.feature")  # new
```

**`test/conftest.py`** — register new step modules (pytest-bdd 8.x requirement):

```python
pytest_plugins = [
    "test.web.steps.login_steps",
    "test.web.steps.transactions_steps",  # new
]
```

API tests need no wiring — pytest discovers them by file/function name under `testpaths`.

### Step 9 — Validate with Playwright CLI (mandatory, this is the second and final automatable check)

Step 3 verified the pieces in isolation; this step proves the assembled framework code — the actual page object/steps/feature or ApiClient/test — works end to end.

```bash
# Web — target only the new scenario, keep artifacts on failure
uv run pytest test/web/ -k "<new scenario keyword>" -v --tracing=retain-on-failure

# API — target the new/changed test file
uv run pytest test/api/<domain>/test_<domain>.py -v
```

If it fails: go back to Step 3 and re-verify against the live app — don't loosen the assertion to make it pass. If the app isn't running (Step 2 was "down"), say so instead of fabricating a pass.

Delete any scratch script from Step 3 once Step 9 passes — it was for verification only, it never gets committed.

### Step 10 — Quality gates

Before finishing:

- [ ] No hardcoded `http://localhost` or ports anywhere (use `WEB_BASE_URL` / `API_BASE_URL`)
- [ ] No locators or `expect()` in step files; no raw `request.get/post` in test files (goes through `ApiClient`)
- [ ] Existing steps/page methods/`ApiClient` methods reused wherever possible — list which were reused vs. new
- [ ] New step text is generic enough for future scenarios
- [ ] `pytest --collect-only test/web/` (and `test/api/` if touched) collects without errors
- [ ] Step 3's live check actually ran and printed a confirmed result — not just read from the diff
- [ ] Step 9's validation run actually passed against the live app — state the command and result, don't just claim it
- [ ] No leftover scratch verification script committed

## Diff lead → confirmed pattern → framework mapping (quick reference)

| Diff/live-check pattern | Web: Page method | Typical step | API: ApiClient method |
|---|---|---|---|
| `goto(url)` | `load()` | `Given I am on the <page> page` | — |
| `data-test="x"` on new element | `_loc_x` property | — | — |
| `fill(..., text)` | `enter_<field>(text)` or combined `do_login(u, p)` | `When I enter ...` | — |
| `click(...)` | `click_<element>()` | `When I click the <element> button` | — |
| `expect(...).to_contain_text` | `check_<what>(expected)` | `Then I should see ...` | — |
| `select_option` | `select_<field>(value)` | `When I select "<value>" from ...` | — |
| `router.get/post("/path", ...)` | — | — | `get_<resource>()` / `post_<resource>(...)` |

## Additional resources

- Full before/after examples, including the diff-driven walkthrough: [examples.md](examples.md)
