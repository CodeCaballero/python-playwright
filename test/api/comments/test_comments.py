def test_get_comments(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    transaction = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA comments test",
            "amount": 100,
        }
    ).json()["transaction"]

    response = client.get_comments(transaction["id"])

    assert response.status == 200
    assert isinstance(response.json()["comments"], list)


def test_get_comments_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_comments("bad!!")

    assert response.status == 422


def test_post_comment(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    transaction = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA post comment",
            "amount": 100,
        }
    ).json()["transaction"]

    response = client.post_comment(transaction["id"], "QA comment test")

    assert response.status == 200
    comments = client.get_comments(transaction["id"]).json()["comments"]
    assert any(comment["content"] == "QA comment test" for comment in comments)


def test_post_comment_validation_error(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    transaction = client.post_transaction(
        {
            "transactionType": "payment",
            "receiverId": second_user["id"],
            "description": "QA invalid comment",
            "amount": 100,
        }
    ).json()["transaction"]

    response = client.post_comment(transaction["id"])

    assert response.status == 422
