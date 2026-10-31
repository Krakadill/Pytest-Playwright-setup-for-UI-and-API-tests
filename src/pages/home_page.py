from playwright.sync_api import Page
from pages.base_page import BasePage
from components.task_form_component import TaskFormComponent


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.new_button = self.page.locator('//button[@data-testid="new-task-button"]')
        self.task_form = TaskFormComponent(page)
        
    def open(self):
        self.goto("/dashboard")

    def create_task(self,title: str):
        self.new_button.click()
