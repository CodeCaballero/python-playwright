import pytest


@pytest.mark.parametrize(
    "username,password,status", [
    ("Reuben97", "s3cret", 200),
    ("Reuben97", "", 400),
    ("Reuben97", "wrong_password", 401),
    ("Reuben97", "password_expired", 401),
    ("user_blocked", "s3cret", 401),
    ("user_expired", "s3cret", 401),
    ("wrong_user", "s3cret", 401),
    ("", "s3cret", 400)
   
])
def test_login(login_client, username, password, status):
    response = login_client.login(username, password)
    assert response.status == status