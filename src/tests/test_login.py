import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.home_page import HomePage
from data.login_data import CREDENTIALS

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {k: v for k, v in browser_context_args.items() if k != "storage_state"}


def test_positive_login(login_page: LoginPage, home_page: HomePage) -> None:
    login_page.login(CREDENTIALS.email, CREDENTIALS.password)

    expect(home_page.new_button).to_be_visible()


def test_negatie_login(login_page: LoginPage, home_page: HomePage) -> None:
    login_page.login('blabla', CREDENTIALS.password)

    expect(home_page.new_button).not_to_be_visible()