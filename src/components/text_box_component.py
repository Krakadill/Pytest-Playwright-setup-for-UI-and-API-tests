from playwright.sync_api import Page


class TextBoxComponent():
    def __init__(self, page: Page):
        self.full_name_input =  page.locator('#userName')
        self.email_input =  page.locator('#userEmail')
        self.current_address_input =  page.locator('#currentAddress')
        self.permanent_address_input =  page.locator('#permanentAddress')
        self.submit_btn = page.locator('#submit')

        self.output = page.locator('#output')
        self.output_name = self.output.locator('#name')
        self.output_email = self.output.locator('#email')
        self.output_current_address = self.output.locator('#currentAddress')
        self.output_permanent_address = self.output.locator('#permanentAddress')

    def fill_form(self, full_name: str, email: str, current_address: str, permanent_address: str) -> None:
        self.full_name_input.fill(full_name)
        self.email_input.fill(email)
        self.current_address_input.fill(current_address)
        self.permanent_address_input.fill(permanent_address)

    def submit_form(self) -> None:
        self.submit_btn.click()

