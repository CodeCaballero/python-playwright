class UserBuilder:
    REQUIRED_FIELDS = {
        "firstName", "lastName", "username", "password",
        "email", "phoneNumber", "avatar", "balance", "defaultPrivacyLevel"
    }
    def __init__(self):
        self.user = {}

    def set_first_name(self, name):
        self.user['firstName'] = name
        return self

    def set_last_name(self, last_name):
        self.user['lastName'] = last_name
        return self

    def set_password(self, password):
        self.user['password'] = password
        return self

    def set_phone_number(self, phone_number):
        self.user['phoneNumber'] = phone_number
        return self

    def set_balance(self, balance):
        self.user['balance'] = balance
        return self

    def set_privacy_level(self, privacy_level):
        self.user['defaultPrivacyLevel'] = privacy_level
        return self

    def build(self):
        self.user["username"] = f"qa_{self.user['firstName']}"
        self.user["email"] = f"{self.user['username']}@test.com"
        self.user["avatar"] = f"https://api.dicebear.com/9.x/pixel-art/svg?seed={self.user['username']}"
        if set(self.user.keys()) != set(self.REQUIRED_FIELDS):
            raise ValueError("Not all required fields are set")
        return dict(self.user)

