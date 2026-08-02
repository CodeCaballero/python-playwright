from pytest_bdd import given, parsers

from test.builder.user_builder import UserBuilder


@given(parsers.parse('A created user named "{name}" with password "{password}"'))
def created_user(name: str, password: str, database_api):
    user = UserBuilder().set_username(name).set_password(password).build_random()
    database_api.create_user(user)
