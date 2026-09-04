def test_list_bank_accounts_without_auth(api_client):
    response = api_client.graphql_list_bank_accounts()

    assert response.status == 200
    assert "errors" in response.json()


def test_list_bank_accounts(api_client_with_auth):
    response = api_client_with_auth("Heath93").graphql_list_bank_accounts()

    assert response.status == 200
    data = response.json()["data"]
    assert isinstance(data["listBankAccount"], list)


def test_create_bank_account(api_client_with_auth):
    response = api_client_with_auth("Heath93").graphql_create_bank_account(
        "QA GraphQL Bank", "123456789", "987654321"
    )

    assert response.status == 200
    account = response.json()["data"]["createBankAccount"]
    assert account["bankName"] == "QA GraphQL Bank"
    assert account["isDeleted"] is False


def test_delete_bank_account(api_client_with_auth):
    client = api_client_with_auth("Heath93")
    created = client.graphql_create_bank_account(
        "QA GraphQL Delete", "111111111", "222222222"
    ).json()["data"]["createBankAccount"]

    response = client.graphql_delete_bank_account(created["id"])

    assert response.status == 200
    assert response.json()["data"]["deleteBankAccount"] is True
