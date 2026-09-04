def test_get_likes(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    transaction = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA likes test",
            "amount": 100,
        }
    ).json()["transaction"]

    response = client.get_likes(transaction["id"])

    assert response.status == 200
    assert isinstance(response.json()["likes"], list)


def test_get_likes_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_likes("bad!!")

    assert response.status == 422


def test_post_like(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    transaction = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA post like",
            "amount": 100,
        }
    ).json()["transaction"]

    response = client.post_like(transaction["id"])

    assert response.status == 200
    likes = client.get_likes(transaction["id"]).json()["likes"]
    assert len(likes) == 1
