import pytest


@pytest.mark.parametrize(
    "entity",
    [
        "users",
        "contacts",
        "bankaccounts",
        "notifications",
        "transactions",
        "likes",
        "comments",
        "banktransfers",
    ],
)
def test_get_test_data_by_entity(api_client, entity):
    response = api_client.get_test_data(entity)

    assert response.status == 200
    assert isinstance(response.json()["results"], list)


def test_get_test_data_invalid_entity(api_client):
    response = api_client.get_test_data("bogus")

    assert response.status == 422
