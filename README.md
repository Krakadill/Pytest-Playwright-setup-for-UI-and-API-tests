# Pytest + Playwright Setup for UI and API Tests

A structured, scalable test automation starter built with **pytest** and **Playwright (Python, sync API)**. It covers both UI tests (Page Object Model) and API tests (`APIRequestContext`), with parallel execution and Allure reporting.

## Features

- **Page Object Model**: pages and reusable components are separated from tests
- **DRY by design**: shared setup lives in fixtures, shared data in one module
- **UI and API tests** in one repository, sharing credentials and configuration
- **Authenticated session reuse**: log in once, save storage state, reuse it across tests
- **Parallel execution** with `pytest-xdist`
- **Allure reporting** with failure screenshots, traces and videos attached
- **Secrets in `.env`**, never in code
- **Task runner** (`poe`) for short, memorable commands

## Project structure

```
my-project/
├── .env                    # real credentials (git-ignored)
├── .env.example            # placeholder values, committed
├── .auth/                  # saved storage state (git-ignored)
├── allure-results/         # raw Allure data (git-ignored)
├── reports/                # pytest-html output (git-ignored)
├── test-results/           # Playwright traces, videos, screenshots (git-ignored)
├── pyproject.toml          # pytest config, markers, poe tasks
├── requirements.txt
└── src/
    ├── components/         # reusable UI components (forms, tables, modals)
    ├── data/
    │   └── login_data.py   # credentials loaded from .env
    ├── pages/              # page objects (BasePage and one class per page)
    └── tests/
        ├── conftest.py     # shared fixtures, global setup, report hooks
        ├── test_login.py   # unauthenticated UI tests
        ├── test_*.py       # authenticated UI tests
        └── test_tasks_api.py   # API tests
```

Every package folder (`pages`, `components`, `data`) contains an `__init__.py`. `pythonpath = ["src"]` in `pyproject.toml` lets tests import with `from pages.login_page import LoginPage`.

## Principles

### Page Object Model

Locators and actions live in classes under `src/pages` and `src/components`. Tests contain steps and assertions only, so a UI change is fixed in one place.

```python
def test_positive_login(login_page, home_page):
    login_page.login(CREDENTIALS.email, CREDENTIALS.password)
    expect(home_page.new_button).to_be_visible()
```

### DRY

- **Fixtures replace `beforeEach`.** Shared fixtures (`login_page`, `home_page`, `api`) live in `src/tests/conftest.py`. A test only gets the setup it requests by name.
- **Single source for data.** Credentials are defined once in `src/data/login_data.py` and imported wherever needed.
- **Cleanup with `yield`.** Fixtures that create data (such as API tasks) delete it afterwards, even when the test fails.

### Global setup (storage state)

pytest has no `globalSetup` config key. The equivalent here is a session-scoped fixture in `conftest.py`:

1. Logs in once through the UI and validates the result
2. Saves cookies and localStorage to `.auth/state.json`
3. Feeds that state to every test through the `browser_context_args` fixture

Tests that must start logged out (such as `test_login.py`) override `browser_context_args` in their own file to drop `storage_state`.

Note: with `pytest-xdist`, a session fixture runs once per worker, so each worker logs in once.

### API tests

API tests use Playwright's `APIRequestContext` through the session-scoped `api` fixture, which logs in via the API and attaches the bearer token to every request. They never request `page`, so no browser is launched for them.

## Requirements

- Python 3.10 or newer
- Node.js (only if you install the Allure CLI through npm)
- Java 8 or newer (required by the Allure CLI)
- Allure CLI

Python packages:

| Package             | Purpose                                             |
| ------------------- | --------------------------------------------------- |
| `pytest-playwright` | Playwright integration, `page` / `browser` fixtures |
| `pytest-xdist`      | Parallel test execution                             |
| `allure-pytest`     | Allure results writer                               |
| `pytest-html`       | Optional single-file HTML report                    |
| `python-dotenv`     | Loads `.env` into environment variables             |
| `poethepoet`        | Task runner (`poe`)                                 |

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Git Bash on Windows: source .venv/Scripts/activate
                                   # PowerShell: .venv\Scripts\Activate.ps1

# 2. Install dependencies and browsers
pip install -r requirements.txt
playwright install                 # Linux/CI: playwright install --with-deps

# 3. Install the Allure CLI
npm install -g allure-commandline  # or: scoop install allure
allure --version

# 4. Configure credentials
cp .env.example .env               # then edit the values
```

`.env`:

```
EMAIL=your-email@example.com
PASSWORD=your-password
```

Set the application URL with `--base-url` in `addopts` inside `pyproject.toml`.

## Commands

| Command          | What it does                               |
| ---------------- | ------------------------------------------ |
| `poe test`       | Run all tests (parallel)                   |
| `poe smoke`      | Run tests marked `@pytest.mark.smoke`      |
| `poe regression` | Run tests marked `@pytest.mark.regression` |
| `poe headed`     | Run with a visible browser                 |
| `poe debug`      | Run serially with the Playwright Inspector |
| `poe report`     | Build and open the Allure report           |

Without poe:

```bash
pytest -n 3                                   # 3 parallel workers
pytest -n auto                                # one worker per CPU core
pytest -n 0 -s --headed                       # serial, visible, with print output
pytest src/tests/test_login.py                # one file
pytest -k "login and positive"                # filter by name
pytest --collect-only -q -n 0                 # list collected tests without running
```

## Reporting and debugging

Run `poe test`, then `poe report`. The Allure report shows results by suite, error details, and attachments on failed tests: screenshot, page URL, trace and video.

If a trace does not open inside Allure, open it directly:

```bash
playwright show-trace test-results/<test-folder>/trace.zip
```

or drag the zip into https://trace.playwright.dev.

Artifacts are kept only for failures (`retain-on-failure`), which keeps runs fast and storage small.

## Conventions

- Test files are named `test_*.py` and test functions `test_*`; anything else is not collected.
- `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Locators belong in page objects and components, not in tests.
- Fixtures are named after what they provide (`login_page`, `home_page`, `api`).
- Register new markers in `pyproject.toml` to avoid warnings.

## CI

Run in any CI with:

```bash
pip install -r requirements.txt
playwright install --with-deps
pytest -n 3
```

Store `EMAIL` and `PASSWORD` as CI secrets, and upload `allure-results/` and `test-results/` as artifacts (`if: always()`).
