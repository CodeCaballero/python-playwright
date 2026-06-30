---
name: playwright-codegen-to-bdd
description: >-
  Adapts Playwright codegen output to the pytest-bdd + Page Object framework
  (features, steps, locators). Prioritizes reusing existing Gherkin steps and
  page methods. Use when the user pastes codegen, asks to convert recording to
  BDD, or wants new web scenarios added from Playwright scripts.
---

# Playwright Codegen → QA Framework (BDD)

Convert Playwright codegen into **pytest-bdd** tests following this project's **layered web architecture**. Never paste codegen raw into steps or features.

## Framework layout (web only)

```
test/web/
├── features/<domain>.feature      # Gherkin scenarios
├── steps/<domain>_steps.py        # @given / @when / @then (thin — call Page Objects)
├── pages/<domain>_page.py       # Locators (@property _loc_*) + actions + assertions
└── test_scenarios.py            # scenarios("<domain>.feature") — add new features here
test/conftest.py                 # pytest_plugins — register new *_steps.py modules
config/settings.py               # WEB_BASE_URL — never hardcode URLs in pages
```

**API tests are out of scope** for this skill (pytest pure, no Gherkin).

## Workflow

Copy this checklist and track progress:

```
Codegen conversion:
- [ ] 1. Parse codegen (actions, locators, URLs, assertions)
- [ ] 2. Inventory existing steps — reuse before creating new ones
- [ ] 3. Decide: extend existing Page Object vs new Page Object
- [ ] 4. Extract locators → page properties
- [ ] 5. Extract actions/assertions → page methods
- [ ] 6. Write Gherkin using reused + new steps only
- [ ] 7. Implement only missing step definitions
- [ ] 8. Register feature in test_scenarios.py + steps in conftest pytest_plugins
- [ ] 9. Verify naming and imports match project conventions
```

### Step 1 — Parse codegen

Identify in order:

| Codegen pattern | Framework target |
|-----------------|------------------|
| `page.goto("http://...")` | `Page.load()` using `WEB_BASE_URL` from `config.settings` |
| `page.get_by_role(...)` | `@property _loc_*` — **prefer get_by_role** over CSS |
| `page.locator("css")` | `@property _loc_*` — prefer `data-test` if present |
| `.fill()`, `.click()` | Page method (`do_login`, `click_submit`, …) |
| `expect(locator).to_*()` | Page assertion method (`check_username`, `assert_visible`, …) |
| `page.wait_for_*` | Inside page method, not in steps |

**Drop from codegen:** imports, browser launch, `context`, hardcoded base URLs, duplicate waits that Playwright auto-waits already cover.

### Step 2 — Reuse existing steps (mandatory first)

Before writing any new step:

1. Read all files in `test/web/steps/`.
2. Read related `test/web/features/*.feature` for step phrasing already in use.
3. Map each codegen action to an **existing** Gherkin step if semantics match.

**Reuse rules:**

- Same user action + same meaning → **reuse exact step text** (e.g. `I click the login button`).
- Same action, different target → **parameterize** with `parsers.parse` and `{name}` placeholders.
- Step exists but page differs → reuse step text; step impl may call the correct Page Object.
- Only create a new step when no existing step covers the intent.

**Anti-pattern:** paraphrasing an existing step (`I press login` vs `I click the login button`) — duplicates break reuse.

### Step 3 — Page Object

**Extend** `LoginPage` (or existing page) when the flow stays on the same screen/domain. **Create** `test/web/pages/<new>_page.py` when navigating to a new area (dashboard, settings, …).

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

**Locator rules:**

- Private properties: `_loc_<element_purpose>` as `@property` returning a Locator.
- Prefer `get_by_role` > `get_by_label` > `data-test` > CSS (codegen CSS is a fallback).
- Assertions use `expect(...)` inside page methods, not in steps.
- Inherit `BasePage`; use `self.page`, `self.navigate_to()`.

### Step 4 — Steps (thin layer)

```python
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page
from test.web.pages.example_page import ExamplePage

@when("I click the submit button")
def click_submit(page: Page):
    ExamplePage(page).click_submit()
```

- Steps receive `page: Page` fixture only (pytest-playwright).
- One step → one page method call. No locators in steps.
- Parameterized: `@when(parsers.parse('I enter "{value}" in the search field'))`.

### Step 5 — Feature file

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
- Scenario names describe **business outcome**, not clicks.
- `And` / `But` continue previous step type in Gherkin.
- Quotes for string parameters matching `parsers.parse` placeholders.

### Step 6 — Wire-up

**`test/web/test_scenarios.py`** — add line per feature file:

```python
from pytest_bdd import scenarios

scenarios("login.feature")
scenarios("dashboard.feature")  # new
```

**`test/conftest.py`** — register new step modules (pytest-bdd 8.x requirement):

```python
pytest_plugins = [
    "test.web.steps.login_steps",
    "test.web.steps.dashboard_steps",  # new
]
```

## Codegen → framework mapping (quick reference)

| Codegen | Page method | Typical step |
|---------|-------------|--------------|
| `goto(url)` | `load()` | `Given I am on the <page> page` |
| `fill(..., text)` | `enter_<field>(text)` or combined `do_login(u, p)` | `When I enter ...` |
| `click(...)` | `click_<element>()` | `When I click the <element> button` |
| `expect(...).to_contain_text` | `check_<what>(expected)` | `Then I should see ...` |
| `select_option` | `select_<field>(value)` | `When I select "<value>" from ...` |

## Quality gates

Before finishing:

- [ ] No hardcoded `http://localhost` in pages (use `WEB_BASE_URL`)
- [ ] No locators or `expect()` in step files
- [ ] Existing steps reused wherever possible; list which were reused vs new
- [ ] New step text is generic enough for future scenarios
- [ ] `pytest --collect-only test/web/` collects new scenarios without errors

## Additional resources

- Full before/after example: [examples.md](examples.md)
