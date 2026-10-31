from playwright.sync_api import Page


class TaskFormComponent():
    def __init__(self, page: Page):
        self.title_input =  page.locator('//input[@id="title"]')
        self.description_input =  page.locator('#description')
        self.priority_input =  page.locator('#priority')
        self.create_button = page.locator('//button[@data-testid="task-submit-button"]')


    def create_new_task(self, title: str, description: str = "", priority:str ="") -> None:
        self.title_input.fill(title)
        self.create_button.click()



       

    

