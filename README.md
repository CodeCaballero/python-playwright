
# 🎭 Playwright Automation Framework

<!-- badges-start -->
[![CI](https://img.shields.io/github/actions/workflow/status/CodeCaballero/python-playwright/ci.yml?branch=main&style=flat&logo=github&label=CI)](https://github.com/CodeCaballero/python-playwright/actions/workflows/ci.yml)
[![Lint](https://img.shields.io/github/actions/workflow/status/CodeCaballero/python-playwright/lint.yml?style=flat&logo=github&label=Lint)](https://github.com/CodeCaballero/python-playwright/actions/workflows/lint.yml)
[![Playwright](https://img.shields.io/badge/Playwright-1.60-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-9.0-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![pytest-bdd](https://img.shields.io/badge/pytest--bdd-8.1-23D96C?logo=cucumber&logoColor=white)](https://pytest-bdd.readthedocs.io/)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-online-FF6A5C?logo=qameta&logoColor=white)](https://codecaballero.github.io/python-playwright/)
<!-- badges-end -->


## Overview
This test automation framework combines the generation of test following the project test pattern (POM) automatically using 
Claude Code, Skills, Playwright-cli, Playwright, pytest, and pytest-bdd to create a comprehensive solution for testing web applications.
This project uses as example the Cypress Real World App, a popular open-source project that provides a realistic web application for testing purposes.

## Key Features

- **AI-Powered Test Generation** — Claude Code, enhanced with custom Skills, translates natural-language specifications into executable test code following Page Object Model pattern    
- **Hybrid test strategy** — Web UI with pytest-bdd (Gherkin) and API tests with plain pytest
- **Page Object Model** — Locators, actions, and assertions live in page objects, isolated from step definitions — following Playwright's POM convention (unlike classic Selenium POM, where assertions typically lived in the step/test layer)
- **Thin BDD steps** — Steps only orchestrate; all Playwright logic lives in page objects
- **Resilient locators** — Prefer `get_by_role` and `get_by_test_id` (`data-test`) (modified playwright configuration)
- **Auth state reuse** — Login once, persist `storage_state` under `.auth/` for faster scenarios
- **Test data seeding** — Using class `UserBuilder` to create users via API
- **Test isolation** — `@reset_db` marker reseeds the database after tagged scenarios
- **Centralized config** — Base URLs and seed users via env vars / `config/`
- **CI/CD pipeline** — Optimized with dependency caching
- **Reporting** — Allure reports published to GitHub Pages; Playwright traces on failure
- **BDD skills** — Skill to convert specification in natural language into framework-compliant tests
- **Known-flaky handling** — Scenarios marked @flaky run once (no rerun, so a real bug can't hide behind a passing retry), never fail the build (`xfail`, non-strict), and are tagged `flaky` in the Allure report
- **Parallelization** — Tests run in parallel to speed up execution time with python-xdist

##  Tech Stack

| Technology             | Purpose                                                              |
|:-----------------------|:---------------------------------------------------------------------|
| **Claude Code**        | AI-powered coding assistant for generating and refining test scripts |
| **Playwright-cli**     | Command interface use by claude code to control the browser          |
| **Playwright**         | E2E test runner and automation library                               |
| **Requests**           | API testing and backend test setup                                   |
| **Python**             | Primary programming language                                         |
| **Gherkin (Cucumber)** | BDD syntax for writing test scenarios                                |
| **Github Actions**     | Continuous integration pipeline                                      |
| **Github Pages**       | Artifact repository for Alure reports                                |
| **Pytest**             | Test runner and orchestration                                        |
| **pytest-bdd**         | BDD integration with Gherkin scenarios                               |
| **pytest-playwright**  | Browser fixtures and Playwright integration for pytest               |



## Installation

### Prerequisites

| Tool    | Version |
|:--------|:--------|
| Python  | 3.12+   |
| [uv](https://github.com/astral-sh/uv) | latest |
| Node.js | 22+     |
| Yarn    | latest  |
| Claude Code | latest  |
| [@playwright/cli](https://www.npmjs.com/package/@playwright/cli) | latest |

Node.js and Yarn are only needed to run `deploy-dev-branch`, which clones and starts the app under test. `@playwright/cli` is used by the `playwright-cli-to-bdd` skill — `npm install -g @playwright/cli@latest` if it's not already on your PATH.

The app under test must be available at:

- **Web:** `http://localhost:3000`
- **API:** `http://localhost:3001`

### 1. Clone this repository

```bash
git clone https://github.com/CodeCaballero/python-playwright.git
cd python-playwright
```

### 2. Create a virtual environment and install dependencies

```bash
uv sync
uv run playwright install chromium
```

### 3. Start the Cypress Real World App

Execute the script, passing the branch you want to test as a parameter (it must exist on [CodeCaballero/cypress-realworld-app](https://github.com/CodeCaballero/cypress-realworld-app), the fork the script clones from):
```bash
./deploy-dev-branch add-button-export
```

`yarn dev` runs in the foreground, so open a new terminal and wait until both `http://localhost:3000` and `http://localhost:3001` respond before continuing.

### 4. Generation of the code

Execute in the Claude Code terminal, e.g.:

```bash
/playwright-cli-to-bdd verify that the CSV file is downloaded, that it is not empty, that it has at least one line, and that it includes the header: Date,Sender,Receiver,Amount,Description,Status.
```

The argument is optional — it defaults to reading `diff.txt`.

### 5. How it works

The deploy script clones the repository, checks out the branch passed as a parameter, deploys the cypress-real-world-app and generates a diff file with
the changes on that branch.

The Claude Code skill uses that `diff.txt` file and the `playwright-cli` tool to navigate through the application and generate the code following the framework's
guidelines.

![](/home/caballero/dev/python-playwright/assets/img2.png)
![](/home/caballero/dev/python-playwright/assets/img3.png)
![](/home/caballero/dev/python-playwright/assets/img4.png)

### 6. Environment variables

Defaults are set in `pyproject.toml`:

| Variable       | Default                 |
|:---------------|:------------------------|
| `WEB_BASE_URL` | `http://localhost:3000` |
| `API_BASE_URL` | `http://localhost:3001` |

Override them when needed:

```bash
WEB_BASE_URL=http://localhost:3000 API_BASE_URL=http://localhost:3001 pytest
```

### 7. Run the tests

```bash
# Full suite
uv run pytest -v

# API only
uv run pytest test/api/ -v

# Web (BDD) only
uv run pytest test/web/ -v

# With Allure results
uv run pytest -v --alluredir=allure-results
allure serve allure-results

# Playwright traces on failure
uv run pytest test/web/ -v --tracing=retain-on-failure
```

### 8. Allure reports

Allure reports are generated and published in https://codecaballero.github.io/python-playwright/
![img.png](assets/img.png)