def test_notifications_list(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_notifications()

    assert response.status == 200
    assert isinstance(response.json()["results"], list)


def test_notifications_list_without_auth(api_client):
    response = api_client.get_notifications()

    assert response.status == 401


def test_post_notifications_bulk(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    transaction = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA notification test",
            "amount": 100,
        }
    ).json()["transaction"]

    response = client.post_notifications_bulk(
        [{"type": "payment", "transactionId": transaction["id"], "status": "received"}]
    )

    assert response.status == 200
    results = response.json()["results"]
    assert results[0]["transactionId"] == transaction["id"]


def test_post_notifications_bulk_validation_error(api_client_with_auth):
    response = api_client_with_auth("Heath93").post_notifications_bulk(
        [{"type": "bogus", "transactionId": "someId"}]
    )

    assert response.status == 422


def test_patch_notification_mark_read(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    transaction = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA mark read",
            "amount": 100,
        }
    ).json()["transaction"]
    notification = client.post_notifications_bulk(
        [{"type": "payment", "transactionId": transaction["id"], "status": "received"}]
    ).json()["results"][0]

    response = client.patch_notification(notification["id"], {"isRead": True})

    assert response.status == 204


def test_patch_notification_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").patch_notification("bad!!", {"isRead": True})

    assert response.status == 422
