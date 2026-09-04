import pytest


def test_bank_accounts_list(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_bank_accounts()

    assert response.status == 200
    assert isinstance(response.json()["results"], list)


def test_bank_accounts_list_without_auth(api_client):
    response = api_client.get_bank_accounts()

    assert response.status == 401


def test_post_bank_account(api_client_with_auth):
    response = api_client_with_auth("Heath93").post_bank_account(
        {"bankName": "QA Bank", "accountNumber": "123456789", "routingNumber": "987654321"}
    )

    assert response.status == 200
    account = response.json()["account"]
    assert account["bankName"] == "QA Bank"
    assert account["isDeleted"] is False


@pytest.mark.parametrize(
    "payload,missing_field",
    [
        ({"bankName": "QA Bank", "accountNumber": "123456789"}, "routingNumber"),
        ({"bankName": "QA Bank", "routingNumber": "987654321"}, "accountNumber"),
        ({"accountNumber": "123456789", "routingNumber": "987654321"}, "bankName"),
    ],
)
def test_post_bank_account_validation_errors(api_client_with_auth, payload, missing_field):
    response = api_client_with_auth("Heath93").post_bank_account(payload)

    assert response.status == 422
    errors = response.json()["errors"]
    assert any(error["param"] == missing_field for error in errors)


def test_get_bank_account_by_id(api_client_with_auth):
    client = api_client_with_auth("Heath93")
    created = client.post_bank_account(
        {"bankName": "QA Bank", "accountNumber": "111111111", "routingNumber": "222222222"}
    ).json()["account"]

    response = client.get_bank_account(created["id"])

    assert response.status == 200
    assert response.json()["account"]["id"] == created["id"]


def test_get_bank_account_by_id_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_bank_account("bad!!")

    assert response.status == 422


def test_delete_bank_account(api_client_with_auth):
    client = api_client_with_auth("Heath93")
    created = client.post_bank_account(
        {"bankName": "QA Bank", "accountNumber": "333333333", "routingNumber": "444444444"}
    ).json()["account"]

    response = client.delete_bank_account(created["id"])

    assert response.status == 200
    updated = client.get_bank_account(created["id"]).json()["account"]
    assert updated["isDeleted"] is True


def test_delete_bank_account_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").delete_bank_account("bad!!")

    assert response.status == 422
