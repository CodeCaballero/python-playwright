from config.settings import API_BASE_URL
from config.users import get_password_user
from playwright.sync_api import Playwright

from test.api.helpers.api_client import ApiClient


def create_transaction(
    client: ApiClient, receiver_username: str, transaction_type: str, amount: str, note: str
) -> dict:
    results = client.get_users_search(receiver_username).json()["results"]
    receiver_id = next(user["id"] for user in results if user["username"] == receiver_username)
    return client.post_transaction(
        {
            "transactionType": transaction_type,
            "receiverId": receiver_id,
            "description": note,
            "amount": int(amount),
        }
    ).json()["transaction"]


def create_transaction_as(
    playwright: Playwright,
    sender: str,
    receiver_username: str,
    transaction_type: str,
    amount: str,
    note: str,
) -> dict:
    request_context = playwright.request.new_context(base_url=API_BASE_URL)
    try:
        client = ApiClient(request_context)
        client.post_login(sender, get_password_user(sender))
        return create_transaction(client, receiver_username, transaction_type, amount, note)
    finally:
        request_context.dispose()
