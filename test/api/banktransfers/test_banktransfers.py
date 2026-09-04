def test_bank_transfers_list(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_bank_transfers()

    assert response.status == 200
    assert isinstance(response.json()["transfers"], list)


def test_bank_transfers_list_without_auth(api_client):
    response = api_client.get_bank_transfers()

    assert response.status == 401
