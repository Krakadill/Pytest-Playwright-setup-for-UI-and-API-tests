from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.locator('//input[@id="email"]')
        self.password_input = page.locator('//input[@id="password"]')
        self.sign_in_button = page.locator('//button[@data-testid="login-submit-button"]')

    def login(self, email: str = "", password: str = "", skip: bool = False) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        if not skip:
            self.sign_in_button.click()

    def open(self):
        self.goto("/login")