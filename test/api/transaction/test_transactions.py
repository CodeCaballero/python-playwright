import pytest


def test_transactions(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_transactions()

    assert response.status == 200
    data = response.json()
    page_data = data.get("pageData")
    assert page_data is not None, "Missing 'pageData' in response"
    assert page_data["page"] == 1, "Default page should be 1"
    assert page_data["limit"] == 10, "Default limit should be 10"
    assert page_data["totalPages"] > 0, "Should have at least 1 page"

    results = data.get("results")
    assert isinstance(results, list), "'results' should be a list"
    assert len(results) == 10, f"Expected 10 transactions per page, got {len(results)}"

    if results:
        first_txn = results[0]
        assert "id" in first_txn, "Transaction missing 'id'"
        assert "amount" in first_txn, "Transaction missing 'amount'"
        assert isinstance(first_txn["amount"], int), "'amount' should be an integer"
        assert "status" in first_txn, "Transaction missing 'status'"
        assert first_txn["status"] in ["pending", "complete"], (
            f"Invalid status: {first_txn['status']}"
        )


def test_transactions_without_auth(api_client):
    response = api_client.get_transactions()

    assert response.status == 401


def test_transactions_contacts(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_transactions_contacts()

    assert response.status == 200
    data = response.json()
    assert "pageData" in data, "Missing 'pageData' in response"
    assert isinstance(data.get("results"), list), "'results' should be a list"


def test_transactions_public(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_transactions_public()

    assert response.status == 200
    data = response.json()
    assert "pageData" in data, "Missing 'pageData' in response"
    assert isinstance(data.get("results"), list), "'results' should be a list"


def test_post_transaction_payment(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")

    response = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA payment test",
            "amount": 500,
        }
    )

    assert response.status == 200
    transaction = response.json()["transaction"]
    assert transaction["receiverId"] == second_user["id"]
    assert transaction["status"] == "complete"


def test_post_transaction_request(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")

    response = client.post_transaction(
        {
            "transactionType": "request",
            "receiverId": second_user["id"],
            "description": "QA request test",
            "amount": 700,
        }
    )

    assert response.status == 200
    transaction = response.json()["transaction"]
    assert transaction["status"] == "pending"
    assert transaction["requestStatus"] == "pending"


@pytest.mark.parametrize(
    "payload,invalid_param",
    [
        ({"transactionType": "payment", "description": "x", "amount": 100}, "receiverId"),
        (
            {"transactionType": "payment", "receiverId": "someId", "description": "x"},
            "amount",
        ),
        (
            {
                "transactionType": "bogus",
                "receiverId": "someId",
                "description": "x",
                "amount": 100,
            },
            "transactionType",
        ),
    ],
)
def test_post_transaction_validation_errors(api_client_with_auth, payload, invalid_param):
    response = api_client_with_auth("Heath93").post_transaction(payload)

    assert response.status == 422
    errors = response.json()["errors"]
    assert any(error["param"] == invalid_param for error in errors)


def test_get_transaction_by_id(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    created = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA get by id",
            "amount": 100,
        }
    ).json()["transaction"]

    response = client.get_transaction(created["id"])

    assert response.status == 200
    assert response.json()["transaction"]["id"] == created["id"]


def test_get_transaction_by_id_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_transaction("not-a-valid-id!!")

    assert response.status == 422


def test_patch_transaction_accept_request(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    created = client.post_transaction(
        {
            "transactionType": "request",
            "receiverId": second_user["id"],
            "description": "QA accept request",
            "amount": 300,
        }
    ).json()["transaction"]

    response = client.patch_transaction(created["id"], {"requestStatus": "accepted"})

    assert response.status == 204
    updated = client.get_transaction(created["id"]).json()["transaction"]
    assert updated["requestStatus"] == "accepted"
    assert updated["status"] == "complete"


def test_patch_transaction_reject_request(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    created = client.post_transaction(
        {
            "transactionType": "request",
            "receiverId": second_user["id"],
            "description": "QA reject request",
            "amount": 300,
        }
    ).json()["transaction"]

    response = client.patch_transaction(created["id"], {"requestStatus": "rejected"})

    assert response.status == 204
    updated = client.get_transaction(created["id"]).json()["transaction"]
    assert updated["requestStatus"] == "rejected"


def test_patch_transaction_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").patch_transaction(
        "bad!!", {"requestStatus": "accepted"}
    )

    assert response.status == 422
