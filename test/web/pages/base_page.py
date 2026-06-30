from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str):
        self.page.goto(url)

    def click(self, selector: str):
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        self.page.fill(selector, text)

    def wait_for_element(self, selector: str, timeout: int = 30000):
        self.page.wait_for_selector(selector, timeout=timeout)

    def get_text(self, selector: str) -> str:
        return self.page.text_content(selector)