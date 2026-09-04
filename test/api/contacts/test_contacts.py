def test_get_contacts_by_username(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_contacts("Heath93")

    assert response.status == 200
    assert isinstance(response.json()["contacts"], list)


def test_post_contact(api_client_with_auth, second_user):
    response = api_client_with_auth("Heath93").post_contact(second_user["id"])

    assert response.status == 200
    assert response.json()["contact"]["contactUserId"] == second_user["id"]


def test_post_contact_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").post_contact("bad!!")

    assert response.status == 422


def test_delete_contact(api_client_with_auth, second_user):
    client = api_client_with_auth("Heath93")
    contact = client.post_contact(second_user["id"]).json()["contact"]

    response = client.delete_contact(contact["id"])

    assert response.status == 200


def test_delete_contact_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").delete_contact("bad!!")

    assert response.status == 422
