import base64
import re
import pytest
from pathlib import Path
from pytest_html import extras
from playwright.sync_api import Page, Browser, expect, APIRequestContext, Playwright
import allure

from data.login_data import CREDENTIALS
from pages.home_page import HomePage
from pages.login_page import LoginPage

AUTH_FILE = Path(__file__).resolve().parents[2] / ".auth" / "state.json"


@pytest.fixture(scope="session")
def global_setup(browser: Browser, base_url: str) -> Path:
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    context = browser.new_context(base_url=base_url)
    page = context.new_page()

    login_page = LoginPage(page)
    home_page = HomePage(page)

    login_page.open()
    page.wait_for_load_state("networkidle")   # let the app hydrate
    login_page.login(CREDENTIALS.email, CREDENTIALS.password)

    page.wait_for_url(lambda url: "/login" not in url, timeout=30_000)
    expect(home_page.new_button).to_be_visible(timeout=15_000)

    context.storage_state(path=AUTH_FILE)
    context.close()
    return AUTH_FILE


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, global_setup: Path) -> dict:
    return {**browser_context_args, "storage_state": str(global_setup)}


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    login_page = LoginPage(page)
    login_page.open()
    return login_page


@pytest.fixture
def home_page(page: Page) -> HomePage:
    home_page = HomePage(page)
    home_page.open()
    return HomePage(page)

def _artifact_dir(item) -> Path | None:
    """Find pytest-playwright's output folder for this test."""
    root = Path(item.config.getoption("--output") or "test-results")
    if not root.exists():
        return None
    target = re.sub(r"[^a-z0-9]", "", item.nodeid.lower())
    for folder in root.iterdir():
        if folder.is_dir() and re.sub(r"[^a-z0-9]", "", folder.name.lower()).startswith(target):
            return folder
    return None


@pytest.fixture(scope="session")
def api(playwright: Playwright, base_url: str):
    api_url = f"{base_url}/api/"   # trailing slash matters, see notes

    auth = playwright.request.new_context(base_url=api_url)
    login = auth.post(
        "auth/login",
        data={"email": CREDENTIALS.email, "password": CREDENTIALS.password},
    )
    assert login.ok, f"API login failed: {login.status} {login.text()}"
    token = login.json()["access_token"]
    auth.dispose()

    context = playwright.request.new_context(
        base_url=api_url,
        extra_http_headers={"Authorization": f"Bearer {token}"},
    )
    yield context
    context.dispose()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # 1. Screenshot while the page is still open
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            try:
                allure.attach(
                    page.screenshot(),
                    name="failure-screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
                allure.attach(page.url, name="page-url", attachment_type=allure.attachment_type.TEXT)
            except Exception:
                pass

    if report.when == "teardown":
        folder = _artifact_dir(item)
        if not folder:
            return
        trace = folder / "trace.zip"
        if trace.exists():
            allure.attach.file(
                str(trace),
                name="trace",
                attachment_type="application/vnd.allure.playwright-trace",
                extension="zip",
            )
        for video in folder.glob("*.webm"):
            allure.attach.file(
                str(video),
                name="video",
                attachment_type=allure.attachment_type.WEBM,
            )