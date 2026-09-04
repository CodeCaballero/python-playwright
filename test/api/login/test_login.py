import pytest


@pytest.mark.parametrize(
    "username,password,status",
    [
        ("Heath93", "s3cret", 200),
        ("Heath93", "", 400),
        ("Heath93", "wrong_password", 401),
        ("Heath93", "password_expired", 401),
        ("user_blocked", "s3cret", 401),
        ("user_expired", "s3cret", 401),
        ("wrong_user", "s3cret", 401),
        ("", "s3cret", 400),
    ],
)
def test_login(api_client, username, password, status):
    response = api_client.post_login(username, password)
    assert response.status == status


def test_check_auth_without_login(api_client):
    response = api_client.get_check_auth()

    assert response.status == 401


def test_check_auth_after_login(api_client_with_auth):
    response = api_client_with_auth("Heath93").get_check_auth()

    assert response.status == 200
    assert response.json()["user"]["username"] == "Heath93"


def test_logout_ends_the_session(api_client_with_auth):
    client = api_client_with_auth("Heath93")

    logout_response = client.post_logout()
    check_auth_response = client.get_check_auth()

    assert logout_response.status == 200
    assert check_auth_response.status == 401


def test_login_without_remember_uses_a_session_cookie(api_client):
    response = api_client.post_login("Heath93", "s3cret")

    assert "Expires=" not in response.headers["set-cookie"]


def test_login_with_remember_extends_the_cookie_expiry(api_client):
    response = api_client.post_login("Heath93", "s3cret", remember=True)

    assert "Expires=" in response.headers["set-cookie"]
