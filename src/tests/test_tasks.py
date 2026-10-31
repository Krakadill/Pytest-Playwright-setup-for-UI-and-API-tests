from playwright.sync_api import Page, expect
from pages.home_page import HomePage

def test_create_new_task (home_page: HomePage, page: Page) -> None:
    home_page.new_button.click()
    home_page.task_form.create_new_task("Brand new task")
    task_title_element = page.locator('//h3[contains(@data-testid, "task-title-") and contains(text(), "Brand new task")]')
    
    expect(task_title_element).not_to_be_empty()