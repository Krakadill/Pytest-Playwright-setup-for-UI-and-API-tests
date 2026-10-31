from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, path: str = "/"):
        self.page.goto(path, wait_until="domcontentloaded")  # resolved against base_url