from config.users import get_password_user


def test_users_list(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_users()

    assert response.status == 200
    assert isinstance(response.json()["results"], list)


def test_users_list_without_auth(api_client):
    response = api_client.get_users()

    assert response.status == 401


def test_users_search(api_client_with_auth, second_user):
    response = api_client_with_auth("Heath93").get_users_search(second_user["username"])

    assert response.status == 200
    results = response.json()["results"]
    assert any(user["id"] == second_user["id"] for user in results)


def test_users_search_missing_query(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_users_search()

    assert response.status == 422


def test_get_user_by_id_own(api_client_with_auth):
    client = api_client_with_auth("Heath93")
    user_id = client.post_login("Heath93", get_password_user("Heath93")).json()["user"]["id"]

    response = client.get_user(user_id)

    assert response.status == 200
    assert response.json()["user"]["id"] == user_id


def test_get_user_by_id_other_user(api_client_with_auth, second_user):
    response = api_client_with_auth("Heath93").get_user(second_user["id"])

    assert response.status == 401


def test_get_user_profile(api_client_with_auth, second_user):
    response = api_client_with_auth("Heath93").get_user_profile(second_user["username"])

    assert response.status == 200
    profile = response.json()["user"]
    assert profile["firstName"] == second_user["firstName"]


def test_patch_user(api_client_with_auth):
    client = api_client_with_auth("Heath93")
    login_response = client.post_login("Heath93", "s3cret")
    user_id = login_response.json()["user"]["id"]

    response = client.patch_user(user_id, {"firstName": "Ted"})

    assert response.status == 204


def test_patch_user_invalid_id(api_client_with_auth):
    response = api_client_with_auth("Heath93").patch_user("bad!!", {"firstName": "Ted"})

    assert response.status == 422
