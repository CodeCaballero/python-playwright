---
name: playwright-cli-to-bdd
description: >
  Reads the argument, because de argument tells what you have to test and check
  Reads a PR diff (default diff.txt) to detect new/changed UI features, 
  then drives the app with `playwright-cli` (the
  agent-oriented CLI, `@playwright/cli` — not `playwright codegen`/`open`)
  against the running app to confirm the real selectors/DOM/response shape
  before writing anything. Converts the confirmed interaction into
  framework-conformant tests: pytest-bdd (features, steps, page objects) for
  frontend changes, plain pytest + ApiClient for backend-only changes.
  Validates the result by running the real test suite with pytest (the
  pytest-playwright plugin) against the running app. Every touchpoint is
  CLI-driven and agent-run Reuses existing steps/page objects/ApiClient methods
  whenever possible. if there is something that fails, dont try to fix, abort and
  explain the problem
---

# Diff → QA Framework (BDD + API)

**Input source:** a PR diff file, default `diff.txt` . The diff tells you **what** changed and roughly **where** — it is never trusted as the final source of truth for a selector.

**Two automated touchpoints, both agent-driven, neither is `codegen`:**

1. **Live verification (Step 3)** — driven with `playwright-cli` (the `@playwright/cli` package, installed as the `.claude/skills/playwright-cli` skill — see its `SKILL.md` for the full command reference) against the real running app, to prove each candidate locator resolves to exactly one element (or, for the API side, that the real endpoint returns the expected shape). This replaces guessing a selector from JSX in the diff — the diff gives you the lead (`data-test="x"`, a button's visible text, a route path), the live CLI session gives you the proof.
2. **Final validation (Step 9)** — running the generated framework tests for real with `uv run pytest ...` (the `pytest-playwright` plugin) against the same running app.

`playwright-cli` is a different, separate tool: every command is a single scripted call that returns short structured text, so it's agent-drivable with no human in the loop — that's why it's used for Step 3 instead of a throwaway Python script.

**Goal:** generate tests that follow the existing layered architecture and conventions — never paste raw Playwright/request code directly into steps, features, or test files.

## Usage

This skill lives at `.claude/skills/playwright-cli-to-bdd/SKILL.md` — that's the path Claude Code auto-discovers project skills from (`.skills/` at the repo root, without `.claude/`, is **not** scanned and will show as an unknown command).

```
/playwright-cli-to-bdd
```

That's the whole invocation — Step 3 (`playwright-cli` live verification) and Step 9 (`pytest` validation) run automatically as part of the workflow below, no separate call needed from you.

Diff path defaults to `diff.txt`. To point at a different one, pass it as the argument — it arrives as `$ARGUMENTS`, use that path instead of the default in Step 1:

```
/playwright-cli-to-bdd path/to/other-diff.txt
```

## Scope: which path does the diff need?

Classify each diff before generating anything:

| Diff touches... | Path |
|---|---|
| `src/**` UI components/containers only | **Web path** — pytest-bdd (feature/steps/page) |


## Architecture

```
test/web/
├── features/<domain>.feature      # Gherkin scenarios
├── steps/<domain>_steps.py        # @given / @when / @then (thin — call Page Objects)
├── pages/<domain>_page.py         # Locators (@property _loc_*) + actions + assertions
└── test_scenarios.py              # scenarios("<domain>.feature") — add new features here
test/conftest.py                   # pytest_plugins — register new *_steps.py modules
config/settings.py                 # WEB_BASE_URL / API_BASE_URL — never hardcode URLs or ports
```

## Workflow

Copy this checklist and track progress — each item maps 1:1 to a section below:

```
[ ] 1.  Read the diff → classify path (Web) and list what changed
[ ] 2.  Check prerequisites — is the app running at WEB_BASE_URL?
[ ] 3.  Verify live — drive playwright-cli against the running app to confirm candidate selectors/endpoint
[ ] 4.  Inventory existing steps/pages (web) or ApiClient methods (api) — reuse first
[ ] 5.  Decide: extend an existing Page Object/ApiClient vs create a new one
[ ] 6.  Implement — locators/actions (web) or client methods (api), using only what Step 3 confirmed
[ ] 7.  Write the Gherkin feature (web) 
[ ] 8.  Wire up — test_scenarios.py + conftest.py pytest_plugins (web only)
[ ] 9.  Validate — run the new test(s) with pytest against the live app
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
```

If it's down, stop and show and error message

### Step 3 — Verify live: drive it, don't guess it

The diff gives you a *lead*, never a confirmed locator. Turn each lead into a candidate, then prove it against the running app with `playwright-cli` — no interactive tool, no recording, just short scripted CLI calls (Step 2 must have confirmed the app is up first). See `.claude/skills/playwright-cli/SKILL.md` for the full command reference; the sequence below is the one this skill actually needs.

**Web — confirm the candidate locator resolves to exactly one element, on the real page, in its real state (e.g. logged in):**

Reuse an existing `.auth/*.json` from `test/web/helpers/auth_state.py` — the same file the framework itself uses — instead of logging in manually through the CLI. If `find` reports 0 or more than 1 match, or the diff's `data-test` doesn't actually appear at runtime (conditional rendering, a wrapper component, a typo), don't fall back to a guessed CSS selector — run `playwright-cli snapshot` (optionally `--depth=N` to keep it small) to see the real accessibility tree and locate the right role/name instead.

**Stale `.auth/*.json` blocking the click (e.g. an unrelated onboarding/setup modal intercepts pointer events):** this is a stale-cookie problem with that specific cached file, not an app bug and not something to route around in the page object. `ensure_user_auth_state` only (re)creates the file `if not state_path.exists()` — a `.auth/<user>.json` committed or left over from an earlier session/DB state can carry cookies that put the real backend account in a state the live app no longer expects. Fix: `rm .auth/<user>.json` and re-run — the next login is a clean, cookie-free session (the private/incognito-mode equivalent) that regenerates the file against current backend state. Re-verify (Step 3) and re-validate (Step 9) after regenerating before concluding the candidate selector/flow itself is broken.

**API — confirm the real endpoint, status code, and response shape.** If a browser session is already open for the web check above, reuse it instead of opening a second one:

Only once Step 3 has actually reported a confirmed match-count/status/shape do you move on — Step 6 implements exactly what was confirmed here, nothing inferred beyond it.

Close the session when done: `playwright-cli close` (or `close-all` if more than one is open). Scratch artifacts from the CLI (snapshots, downloaded files, console logs) land in `.playwright-cli/`, already gitignored — no manual cleanup required, though `rm -rf .playwright-cli` before the next run keeps things tidy.

### Step 4 — Reuse existing code (mandatory before writing anything new)

**Web:** read every file in `test/web/steps/` and the related `.feature` files for phrasing already in use.

Reuse rules:
- Same user action + same meaning → reuse the exact step text (e.g., `I click the login button`).
- Same action, different target → parametrize with `parsers.parse` and `{name}` placeholders.
- Same endpoint, different inputs → add a case to an existing `@pytest.mark.parametrize` table (see `test_login.py`) instead of a new test function.
- Only create new steps/methods/tests when nothing existing covers the intent.

Anti-pattern: paraphrasing an existing step or duplicating an method under a new name.

### Step 5 — Extend vs. create

- **Web:** extend the current Page Object when the flow stays on the same screen/domain; create `test/web/pages/<new>_page.py` when navigating to a new area.

### Step 6 — Implement

Use only what Step 3 actually confirmed — the CLI's reported match-count/status/shape, not what the diff seemed to imply.

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

**Preconditions: API/DB, never the UI.** If a scenario needs state that isn't itself the behavior under test (a transaction to comment/like/view, a bank account to delete, a pending request to accept/reject, a second user to interact with), create that state directly against the backend in a `Given` step — never by driving the UI through an unrelated create flow first. Driving the UI for setup adds time and flaky surface for zero coverage: the create flow already has its own scenario. Two patterns, pick based on who the acting user is:
- **Setup actor == the user under test** (already logged in via `Given the user "X" is logged in`, so the `page` fixture exists and carries the session cookies): reuse those cookies with `ApiClient(page.context.request, base_url=API_BASE_URL)` — no extra login needed. See `a_payment_already_exists` / `bank_account_already_exists` in `transactions_steps.py` / `bank_accounts_steps.py`.
- **Setup actor != the user under test** (e.g. another user sends the pending request the logged-in user will act on): open an independent `playwright.request.new_context(base_url=API_BASE_URL)`, log in as that other user with `ApiClient.post_login`, do the setup, `.dispose()` the context. See `a_pending_payment_request` in `transactions_steps.py`. This works regardless of Given-step order since it doesn't touch the `page` fixture.

**Don't inline the setup logic in the step once it's more than a single `ApiClient` call.** Looking a receiver up by username, building the payload, and managing the request-context lifecycle is business logic, not step-glue — and it does not belong in `ApiClient` either (its own rule is one method per endpoint, no branching/lookup logic inside it). Put it in a helper module under `test/web/helpers/` instead — same role `auth_state.py` already plays for login setup. See `test/web/helpers/transaction_fixtures.py` (`create_transaction(client, ...)` for the same-actor case, `create_transaction_as(playwright, sender, ...)` for the different-actor case, the latter calling the former after logging in). The `Given` step should then be a one-or-two-line call into the helper, mirroring how a UI step is a one-line call into a Page Object. Extract as soon as the same lookup/payload logic would otherwise be copy-pasted into a second step — don't wait for a third repetition.

When the setup call returns an id you'll need later (e.g. the created transaction), give the `Given` step a `target_fixture` and return it — a later step can then jump straight to it (e.g. `TransactionsPage.load_transaction(id)`) instead of searching the UI by text.

The one exception: when the precondition-looking step *is* the behavior under test (creating a payment is what "Send a payment" verifies), it stays UI-driven — don't move the thing being tested behind an API call.

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

**`test/conftest.py`** — register new step modules (pytest-bdd 8.x requirement):

API tests need no wiring — pytest discovers them by file/function name under `testpaths`.

### Step 9 — Validate with pytest (mandatory, this is the second and final automatable check)

Step 3 (via `playwright-cli`) verified the pieces in isolation; this step proves the assembled framework code — the actual page object/steps/feature or ApiClient/test — works end to end, run through `pytest` and the `pytest-playwright` plugin (a different tool from the `playwright-cli` used in Step 3).

```bash
# Web — target only the new scenario, keep artifacts on failure
uv run pytest test/web/ -k "<new scenario keyword>" -v --tracing=retain-on-failure

# API — target the new/changed test file
uv run pytest test/api/<domain>/test_<domain>.py -v
```

If it fails because an unrelated modal (e.g. onboarding) intercepts the click: check whether it's a stale `.auth/*.json` first (see Step 3) — delete and let it regenerate, then re-run once before treating it as a real failure.

If it still fails: shown an error and abort

Close any `playwright-cli` session still open from Step 3 (`playwright-cli close-all`) once Step 9 passes — nothing from that step gets committed.

### Step 10 — Quality gates

Before finishing:

- [ ] No hardcoded `http://localhost` or ports anywhere (use `WEB_BASE_URL` / `API_BASE_URL`)
- [ ] No locators or `expect()` in step files; no raw `request.get/post` in test files (goes through `ApiClient`)
- [ ] New step text is generic enough for future scenarios
- [ ] Preconditions unrelated to the behavior under test are created via API/DB (`page.context.request` or a fresh `playwright.request` context), not by driving the UI through another create flow first — and that setup logic lives in a `test/web/helpers/` helper, not inlined/duplicated across steps
- [ ] `pytest --collect-only test/web/` collects without errors
- [ ] Step 3's live check actually ran (`playwright-cli`,) and reported a confirmed result — not just read from the diff
- [ ] Step 9's validation run actually passed against the live app — state the command and result, don't just claim it
- [ ] No leftover `playwright-cli` sessions left open, and no ad-hoc verification script (if one was used for an API-only check) committed

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
- `playwright-cli` command reference (used for Step 3): `.claude/skills/playwright-cli/SKILL.md`
