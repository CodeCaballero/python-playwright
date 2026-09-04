from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from test.web.pages.bank_accounts_page import BankAccountsPage


@given("I am on the bank accounts page")
def go_to_bank_accounts(page: Page):
    BankAccountsPage(page).load()


@when("I click create bank account")
def click_create_bank_account(page: Page):
    BankAccountsPage(page).click_create()


@when(
    parsers.parse(
        'I fill the bank account form with bank name "{bank_name}", '
        'routing number "{routing_number}" and account number "{account_number}"'
    )
)
def fill_bank_account_form(page: Page, bank_name: str, routing_number: str, account_number: str):
    BankAccountsPage(page).fill_form(bank_name, routing_number, account_number)


@when(
    parsers.parse(
        'I fill the bank account form with bank name "{bank_name}" and account number '
        '"{account_number}", leaving the routing number blank'
    )
)
def fill_bank_account_form_no_routing(page: Page, bank_name: str, account_number: str):
    BankAccountsPage(page).fill_form(bank_name=bank_name, account_number=account_number)


@when(
    parsers.parse(
        'I fill the bank account form with bank name "{bank_name}" and routing number '
        '"{routing_number}", leaving the account number blank'
    )
)
def fill_bank_account_form_no_account(page: Page, bank_name: str, routing_number: str):
    BankAccountsPage(page).fill_form(bank_name=bank_name, routing_number=routing_number)


@when("I save the bank account")
def save_bank_account(page: Page):
    BankAccountsPage(page).click_save()


@then(parsers.parse('I should see the bank account "{bank_name}" in the list'))
def check_bank_account_in_list(page: Page, bank_name: str):
    BankAccountsPage(page).check_account_in_list(bank_name)


@then(parsers.parse('I should see the bank account validation error "{message}"'))
def check_bank_account_validation_error(page: Page, message: str):
    bank_accounts_page = BankAccountsPage(page)
    bank_accounts_page.check_validation_error(message)
    bank_accounts_page.check_save_disabled()


@when(parsers.parse('I delete the bank account "{bank_name}"'))
def delete_bank_account(page: Page, bank_name: str):
    BankAccountsPage(page).delete_account(bank_name)


@then(parsers.parse('the bank account "{bank_name}" should be marked as deleted'))
def check_bank_account_deleted(page: Page, bank_name: str):
    BankAccountsPage(page).check_account_deleted(bank_name)
