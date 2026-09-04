from config.settings import WEB_BASE_URL
from playwright.sync_api import expect

from test.web.pages.base_page import BasePage


class BankAccountsPage(BasePage):
    @property
    def _loc_create_link(self):
        return self.page.get_by_role("link", name="Create")

    @property
    def _loc_bank_name_input(self):
        return self.page.get_by_role("textbox", name="Bank Name")

    @property
    def _loc_routing_number_input(self):
        return self.page.get_by_role("textbox", name="Routing Number")

    @property
    def _loc_account_number_input(self):
        return self.page.get_by_role("textbox", name="Account Number")

    @property
    def _loc_form_heading(self):
        return self.page.get_by_role("heading", name="Create Bank Account")

    @property
    def _loc_save_button(self):
        return self.page.get_by_test_id("bankaccount-submit")

    def load(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/bankaccounts")

    def click_create(self):
        self._loc_create_link.click()

    def fill_form(self, bank_name: str = "", routing_number: str = "", account_number: str = ""):
        self._loc_bank_name_input.fill(bank_name)
        self._loc_routing_number_input.fill(routing_number)
        self._loc_account_number_input.fill(account_number)
        self._loc_form_heading.click()

    def click_save(self):
        self._loc_save_button.click()

    def check_save_disabled(self):
        expect(self._loc_save_button).to_be_disabled()

    def check_validation_error(self, message: str):
        expect(self.page.get_by_text(message)).to_be_visible()

    def check_account_in_list(self, bank_name: str):
        expect(
            self.page.get_by_test_id("bankaccount-list").get_by_text(bank_name, exact=True)
        ).to_be_visible()

    def delete_account(self, bank_name: str):
        self.page.get_by_role("listitem").filter(has_text=bank_name).get_by_test_id(
            "bankaccount-delete"
        ).click()

    def check_account_deleted(self, bank_name: str):
        expect(self.page.get_by_text(f"{bank_name} (Deleted)")).to_be_visible()
