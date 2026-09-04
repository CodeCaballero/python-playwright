from config.settings import API_BASE_URL
from config.users import get_password_user
from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from test.api.helpers.api_client import ApiClient
from test.web.pages.transactions_page import TransactionsPage


@given("I am on the personal transactions page")
def go_to_personal_transactions(page: Page):
    TransactionsPage(page).load_personal()


@when("I click the export button")
def click_export_button(page: Page):
    TransactionsPage(page).click_export()


@then(
    parsers.parse(
        'the downloaded CSV file "{filename}" should include the header "{header}"'
    )
)
def check_csv_header(page: Page, filename: str, header: str):
    TransactionsPage(page).check_csv_downloaded_with_header(filename, header)


@when("I go to the new transaction page")
def go_to_new_transaction(page: Page):
    TransactionsPage(page).load_new_transaction()


@when("I go to the public transactions feed")
def go_to_public_feed(page: Page):
    TransactionsPage(page).load_public()


@when("I go to the friends transactions feed")
def go_to_friends_feed(page: Page):
    TransactionsPage(page).load_friends()


@when(parsers.parse('I send a payment of "{amount}" to "{receiver_name}" with note "{note}"'))
def send_payment(page: Page, amount: str, receiver_name: str, note: str):
    TransactionsPage(page).send_payment(receiver_name, amount, note)


@when(
    parsers.parse('I request a payment of "{amount}" from "{receiver_name}" with note "{note}"')
)
def send_request(page: Page, amount: str, receiver_name: str, note: str):
    TransactionsPage(page).send_request(receiver_name, amount, note)


@then(parsers.parse('I should see the transaction confirmation "{text}"'))
def check_transaction_confirmation(page: Page, text: str):
    TransactionsPage(page).check_transaction_confirmation(text)


@when("I return to the transactions list")
def return_to_transactions(page: Page):
    TransactionsPage(page).click_return_to_transactions()


@when(parsers.parse('I open the transaction "{description}"'))
def open_transaction(page: Page, description: str):
    TransactionsPage(page).open_transaction_by_description(description)


@then(parsers.parse('I should see the transaction detail for "{description}"'))
def check_transaction_detail(page: Page, description: str):
    TransactionsPage(page).check_transaction_detail_visible(description)


@then("I should see transactions in the feed")
def check_feed_has_transactions(page: Page):
    TransactionsPage(page).check_feed_has_transactions()


@when("I like the transaction")
def like_transaction(page: Page):
    TransactionsPage(page).click_like()


@then(parsers.parse("the transaction like count should be {count:d}"))
def check_like_count(page: Page, count: int):
    TransactionsPage(page).check_like_count(count)


@when(parsers.parse('I add the comment "{content}"'))
def add_comment(page: Page, content: str):
    TransactionsPage(page).add_comment(content)


@then(parsers.parse('I should see the comment "{content}"'))
def check_comment_visible(page: Page, content: str):
    TransactionsPage(page).check_comment_visible(content)


@when("I accept the payment request")
def accept_request(page: Page):
    TransactionsPage(page).click_accept_request()


@when("I reject the payment request")
def reject_request(page: Page):
    TransactionsPage(page).click_reject_request()


@then("the request action buttons should no longer be visible")
def check_request_buttons_hidden(page: Page):
    TransactionsPage(page).check_request_action_buttons_hidden()


@when(parsers.parse("I filter transactions from the last {days:d} days"))
def filter_by_last_n_days(page: Page, days: int):
    TransactionsPage(page).filter_by_last_n_days(days)


@then(parsers.parse("the date filter should show the last {days:d} days"))
def check_date_filter_applied(page: Page, days: int):
    TransactionsPage(page).check_date_filter_applied(days)


@when(parsers.parse('I search for the user "{full_name}"'))
def search_for_user(page: Page, full_name: str):
    TransactionsPage(page).search_user(full_name)


@then(parsers.parse('I should see only "{full_name}" in the search results'))
def check_single_search_result(page: Page, full_name: str):
    TransactionsPage(page).check_single_search_result(full_name)


@then("I should see no search results")
def check_no_search_results(page: Page):
    TransactionsPage(page).check_no_search_results()


@given(
    parsers.parse(
        'a pending payment request of "{amount}" from "{sender}" to "{receiver}" '
        'with note "{note}"'
    )
)
def a_pending_payment_request(playwright, sender: str, receiver: str, amount: str, note: str):
    request_context = playwright.request.new_context(base_url=API_BASE_URL)
    try:
        client = ApiClient(request_context)
        client.post_login(sender, get_password_user(sender))
        results = client.get_users_search(receiver).json()["results"]
        receiver_id = next(user["id"] for user in results if user["username"] == receiver)
        client.post_transaction(
            {
                "transactionType": "request",
                "receiverId": receiver_id,
                "description": note,
                "amount": int(amount),
            }
        )
    finally:
        request_context.dispose()
