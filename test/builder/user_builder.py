import random


class UserBuilder:
    REQUIRED_FIELDS = (
        "firstName",
        "lastName",
        "username",
        "password",
        "email",
        "phoneNumber",
        "avatar",
        "balance",
        "defaultPrivacyLevel",
    )

    def __init__(self):
        self.user = {}

    def set_first_name(self, name):
        self.user["firstName"] = name
        return self

    def set_last_name(self, last_name):
        self.user["lastName"] = last_name
        return self

    def set_password(self, password):
        self.user["password"] = password
        return self

    def set_balance(self, balance):
        self.user["balance"] = balance
        return self

    def set_privacy_level(self, privacy_level):
        self.user["defaultPrivacyLevel"] = privacy_level
        return self

    def set_username(self, username):
        self.user["username"] = username
        return self

    def set_email(self, email):
        self.user["email"] = email
        return self

    def set_avatar(self, avatar):
        self.user["avatar"] = avatar
        return self

    def set_phone_number(self, phone_number):
        self.user["phoneNumber"] = phone_number
        return self

    def _check_fields(self):
        missing_fields = set(self.REQUIRED_FIELDS) - set(self.user.keys())
        if missing_fields:
            raise ValueError(
                f"Not all required fields are set. Required fields: {self.REQUIRED_FIELDS}."
                f" Missing fields: {missing_fields}"
            )

    def build(self):
        self._check_fields()
        return dict(self.user)

    def build_random(self):
        self.user["firstName"] = f"qa_{self.user['username']}"
        self.user["lastName"] = f"last_{self.user['firstName']}"
        self.user["email"] = f"{self.user['username']}@test.com"
        self.user["avatar"] = (
            f"https://api.dicebear.com/9.x/pixel-art/svg?seed={self.user['username']}"
        )
        self.user["defaultPrivacyLevel"] = "public"
        self.user["balance"] = 0
        self.user["phoneNumber"] = f"+{random.randint(1000000000, 9999999999)}"
        self._check_fields()
        return dict(self.user)
